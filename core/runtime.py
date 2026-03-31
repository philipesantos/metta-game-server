import re
import signal
from contextlib import contextmanager
from dataclasses import dataclass
from threading import Lock
from threading import current_thread, main_thread
from typing import Any, Callable

from core.metta_doc_catalog import build_metta_doc_catalog, resolve_metta_doc_ids
from core.nlp.command_catalog import build_command_catalog
from core.patterns.events.startup_event_pattern import StartupEventPattern
from core.patterns.facts.game_over_fact_pattern import GameOverFactPattern
from core.patterns.facts.game_won_fact_pattern import GameWonFactPattern
from core.patterns.functions.synchronize_tick_function_pattern import (
    SynchronizeTickFunctionPattern,
)
from core.patterns.functions.trigger_function_pattern import TriggerFunctionPattern
from core.patterns.wrappers.state_wrapper_pattern import StateWrapperPattern
from core.world_builder import build_world
from utils.response import collect_raw_metta_output, format_metta_output


def _build_metta():
    try:
        from hyperon import MeTTa
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "GameSession requires the 'hyperon' package to be installed."
        ) from exc
    return MeTTa()


def _load_embedding_index_class():
    try:
        from core.nlp.embedding_index import EmbeddingIndex
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "GameSession requires NLP dependencies such as 'numpy' and "
            "'sentence-transformers' to be installed."
        ) from exc
    return EmbeddingIndex


def unwrap_atom(atom) -> str:
    if hasattr(atom, "get_object"):
        obj = atom.get_object()
        if hasattr(obj, "value"):
            return str(obj.value)
        if hasattr(obj, "content"):
            return str(obj.content)
        return str(obj)
    if hasattr(atom, "get_name"):
        return atom.get_name()
    return str(atom)


def end_state(metta) -> tuple[str, str] | None:
    for event_name, pattern in (
        ("game_won", GameWonFactPattern("$reason")),
        ("game_over", GameOverFactPattern("$reason")),
    ):
        result = metta.run(
            f"!(match &self {StateWrapperPattern(pattern).to_metta()} $reason)"
        )
        if result and result[0]:
            return event_name, unwrap_atom(result[0][0])
    return None


def end_state_message(metta) -> str | None:
    resolved = end_state(metta)
    if resolved is None:
        return None
    _, message = resolved
    return message


def _move_summary(move_count: int) -> str:
    noun = "move" if move_count == 1 else "moves"
    return f"You won in {move_count} {noun}."


def _game_over_summary(move_count: int) -> str:
    noun = "move" if move_count == 1 else "moves"
    return f"Game over in {move_count} {noun}."


def _decorate_end_state_message(
    event_name: str | None, message: str | None, move_count: int
) -> str | None:
    if message is None:
        return None
    if event_name == "game_won":
        summary = _move_summary(move_count)
    elif event_name == "game_over":
        summary = _game_over_summary(move_count)
    else:
        return message
    if message == summary or message.endswith(summary):
        return message
    return f"{message}\n{summary}"


@dataclass(frozen=True)
class QueryExecution:
    command_type: str
    original_input: str
    matched_metta: str | None
    doc_ids: tuple[str, ...] = ()
    original_responses: tuple[str, ...] = ()
    responses: tuple[str, ...] = ()


@dataclass(frozen=True)
class CommandResult:
    ok: bool
    input_text: str
    command_type: str
    output: str = ""
    tick_output: str = ""
    error: str | None = None
    end_state_event: str | None = None
    end_state_message: str | None = None
    metta_query: str | None = None
    matched_utterance: str | None = None
    matched_metta: str | None = None
    match_score: float | None = None
    queries: tuple[QueryExecution, ...] = ()


def _output_lines(text: str) -> tuple[str, ...]:
    if not text:
        return ()
    return tuple(line for line in text.splitlines() if line)


def _append_unique_message(responses: tuple[str, ...], message: str | None) -> tuple[str, ...]:
    if not message:
        return responses
    if message in responses:
        return responses
    return responses + (message,)


def _format_metta_error(exc: Exception) -> str:
    detail = str(exc).strip()
    if not detail:
        return "Malformed MeTTa command."
    return f"Malformed MeTTa command: {detail}"


_UNMATCHED_COMMAND_MESSAGE = (
    "That makes no sense here."
)

_EXPLICIT_METTA_DENYLIST = frozenset(
    {
        "import!",
        "bind!",
        "py-atom",
        "py-dot",
        "load-ascii",
    }
)

_METTA_TOKEN_PATTERN = re.compile(r"[^\s()]+")


class MettaExecutionTimeoutError(TimeoutError):
    pass


def _strip_metta_strings_and_comments(source: str) -> str:
    result: list[str] = []
    in_string = False
    in_comment = False
    escaping = False

    for char in source:
        if in_comment:
            if char == "\n":
                in_comment = False
                result.append(char)
            continue
        if in_string:
            if escaping:
                escaping = False
                continue
            if char == "\\":
                escaping = True
                continue
            if char == '"':
                in_string = False
            continue
        if char == ";":
            in_comment = True
            continue
        if char == '"':
            in_string = True
            continue
        result.append(char)

    return "".join(result)


def _find_denied_metta_tokens(query: str) -> tuple[str, ...]:
    seen: list[str] = []
    for token in _METTA_TOKEN_PATTERN.findall(_strip_metta_strings_and_comments(query)):
        if token in _EXPLICIT_METTA_DENYLIST and token not in seen:
            seen.append(token)
    return tuple(seen)


def _format_denied_metta_error(tokens: tuple[str, ...]) -> str:
    if len(tokens) == 1:
        return f"Explicit MeTTa command uses forbidden token: {tokens[0]}."
    return (
        "Explicit MeTTa command uses forbidden tokens: "
        + ", ".join(tokens)
        + "."
    )


def _format_metta_timeout(seconds: float) -> str:
    formatted = format(seconds, "g")
    noun = "second" if formatted == "1" else "seconds"
    return f"MeTTa command timed out after {formatted} {noun}."


@contextmanager
def _metta_timeout(seconds: float | None):
    if seconds is None or seconds <= 0:
        yield
        return
    if current_thread() is not main_thread():
        yield
        return

    previous_handler = signal.getsignal(signal.SIGALRM)

    def _handle_timeout(_signum, _frame):
        raise MettaExecutionTimeoutError()

    signal.signal(signal.SIGALRM, _handle_timeout)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous_handler)


def _run_metta_with_timeout(metta, query: str, *, timeout_seconds: float | None):
    with _metta_timeout(timeout_seconds):
        return metta.run(query)


class GameSession:
    def __init__(
        self,
        *,
        metta_factory: Callable[[], Any] | None = None,
        world_builder: Callable[[], Any] = build_world,
        embedding_index_cls=None,
        model_name: str = "BAAI/bge-small-en-v1.5",
        min_score: float = 0.55,
        min_margin: float = 0.06,
        high_confidence_score: float = 0.82,
        explicit_metta_timeout_seconds: float = 3.0,
    ):
        self._lock = Lock()
        metta_factory = metta_factory or _build_metta
        embedding_index_cls = embedding_index_cls or _load_embedding_index_class()
        self.metta = metta_factory()
        self.world = world_builder()
        self.metta_code = self.world.to_metta()
        self.metta_docs = build_metta_doc_catalog(self.world)
        self.world_load_output = self.metta.run(self.metta_code)
        self.command_catalog = build_command_catalog(self.world, self.metta)
        self.embedding_index = embedding_index_cls(
            self.command_catalog,
            model_name=model_name,
            min_score=min_score,
            min_margin=min_margin,
            high_confidence_score=high_confidence_score,
        )
        self.move_count = 0
        self.startup_query = (
            f"!{TriggerFunctionPattern(StartupEventPattern()).to_metta()}"
        )
        self.explicit_metta_timeout_seconds = explicit_metta_timeout_seconds
        startup_raw_output = self.metta.run(self.startup_query)
        self.startup_output = format_metta_output(startup_raw_output)
        startup_end_state = end_state(self.metta)
        startup_event = startup_end_state[0] if startup_end_state else None
        startup_message = _decorate_end_state_message(
            startup_event,
            startup_end_state[1] if startup_end_state else None,
            self.move_count,
        )
        startup_responses = _append_unique_message(
            _output_lines(self.startup_output), startup_message
        )
        self.startup_result = CommandResult(
            ok=True,
            input_text=self.startup_query,
            command_type="metta",
            output=self.startup_output,
            end_state_event=startup_event,
            end_state_message=startup_message,
            metta_query=self.startup_query,
            queries=(
                QueryExecution(
                    command_type="metta",
                    original_input=self.startup_query,
                    matched_metta=self.startup_query,
                    doc_ids=resolve_metta_doc_ids(self.startup_query, self.metta_docs),
                    original_responses=collect_raw_metta_output(startup_raw_output),
                    responses=startup_responses,
                ),
            ),
        )

    def get_end_state_message(self) -> str | None:
        return end_state_message(self.metta)

    def refresh_command_catalog(self) -> None:
        self.command_catalog = build_command_catalog(self.world, self.metta)
        self.embedding_index.update_entries(self.command_catalog)

    def process_command(
        self, user_query: str, *, command_type: str = "auto"
    ) -> CommandResult:
        stripped = user_query.strip()
        if not stripped:
            resolved_type = (
                "metta"
                if self._normalize_command_type(command_type, user_query) == "metta"
                else "natural_language"
            )
            return CommandResult(
                ok=False,
                input_text=user_query,
                command_type=resolved_type,
                error="Command cannot be empty.",
                queries=(
                        QueryExecution(
                            command_type=resolved_type,
                            original_input=user_query,
                            matched_metta=None,
                            doc_ids=(),
                            original_responses=(),
                            responses=("Command cannot be empty.",),
                        ),
                    ),
                )

        with self._lock:
            resolved_type = self._normalize_command_type(command_type, stripped)
            stopped_state = end_state(self.metta)
            if stopped_state is not None:
                stopped_event, stopped_message = stopped_state
                return CommandResult(
                    ok=False,
                    input_text=user_query,
                    command_type=resolved_type,
                    output=stopped_message,
                    end_state_event=stopped_event,
                    end_state_message=stopped_message,
                    error="The game has already ended.",
                    queries=(
                        QueryExecution(
                            command_type=resolved_type,
                            original_input=user_query,
                            matched_metta=None,
                            doc_ids=(),
                            original_responses=(),
                            responses=(stopped_message,),
                        ),
                    ),
                )

            if resolved_type == "metta":
                metta_query = stripped
                matched_utterance = None
                matched_metta = None
                match_score = None
                denied_tokens = _find_denied_metta_tokens(metta_query)
                if denied_tokens:
                    error_message = _format_denied_metta_error(denied_tokens)
                    return CommandResult(
                        ok=False,
                        input_text=user_query,
                        command_type=resolved_type,
                        error=error_message,
                        metta_query=metta_query,
                        queries=(
                            QueryExecution(
                                command_type=resolved_type,
                                original_input=user_query,
                                matched_metta=metta_query,
                                doc_ids=resolve_metta_doc_ids(
                                    metta_query, self.metta_docs
                                ),
                                original_responses=(error_message,),
                                responses=(),
                            ),
                        ),
                    )
            else:
                self.refresh_command_catalog()
                match = self.embedding_index.match(stripped)
                if match is None:
                    return CommandResult(
                        ok=False,
                        input_text=user_query,
                        command_type=resolved_type,
                        error=_UNMATCHED_COMMAND_MESSAGE,
                        queries=(
                            QueryExecution(
                                command_type=resolved_type,
                                original_input=user_query,
                                matched_metta=None,
                                doc_ids=(),
                                original_responses=(),
                                responses=(_UNMATCHED_COMMAND_MESSAGE,),
                            ),
                        ),
                    )
                metta_query = f"!{match.entry.metta}"
                matched_utterance = match.entry.utterance
                matched_metta = match.entry.metta
                match_score = match.score

            try:
                if resolved_type == "metta":
                    result_output = _run_metta_with_timeout(
                        self.metta,
                        metta_query,
                        timeout_seconds=self.explicit_metta_timeout_seconds,
                    )
                else:
                    result_output = self.metta.run(metta_query)
            except MettaExecutionTimeoutError:
                error_message = _format_metta_timeout(
                    self.explicit_metta_timeout_seconds
                )
                return CommandResult(
                    ok=False,
                    input_text=user_query,
                    command_type=resolved_type,
                    error=error_message,
                    metta_query=metta_query,
                    queries=(
                        QueryExecution(
                            command_type=resolved_type,
                            original_input=user_query,
                            matched_metta=metta_query,
                            doc_ids=resolve_metta_doc_ids(metta_query, self.metta_docs),
                            original_responses=(error_message,),
                            responses=(),
                        ),
                    ),
                )
            except Exception as exc:
                if resolved_type != "metta":
                    raise
                error_message = _format_metta_error(exc)
                return CommandResult(
                    ok=False,
                    input_text=user_query,
                    command_type=resolved_type,
                    error=error_message,
                    metta_query=metta_query,
                    queries=(
                        QueryExecution(
                            command_type=resolved_type,
                            original_input=user_query,
                            matched_metta=metta_query,
                            doc_ids=resolve_metta_doc_ids(metta_query, self.metta_docs),
                            original_responses=(error_message,),
                            responses=(),
                        ),
                    ),
                )

            self.move_count += 1
            raw_result_output = collect_raw_metta_output(result_output)
            formatted_output = format_metta_output(result_output)
            finished_state = end_state(self.metta)
            if finished_state is not None:
                finished_event = finished_state[0]
                finished_message = _decorate_end_state_message(
                    finished_event,
                    finished_state[1],
                    self.move_count,
                )
                query_outputs = _append_unique_message(
                    _output_lines(formatted_output), finished_message
                )
                return CommandResult(
                    ok=True,
                    input_text=user_query,
                    command_type=resolved_type,
                    output=finished_message,
                    end_state_event=finished_event,
                    end_state_message=finished_message,
                    metta_query=metta_query,
                    matched_utterance=matched_utterance,
                    matched_metta=matched_metta,
                    match_score=match_score,
                    queries=(
                        QueryExecution(
                            command_type=resolved_type,
                            original_input=user_query,
                            matched_metta=metta_query,
                            doc_ids=resolve_metta_doc_ids(metta_query, self.metta_docs),
                            original_responses=raw_result_output,
                            responses=query_outputs,
                        ),
                    ),
                )

            if resolved_type == "metta":
                return CommandResult(
                    ok=True,
                    input_text=user_query,
                    command_type=resolved_type,
                    output=formatted_output,
                    end_state_event=None,
                    end_state_message=None,
                    metta_query=metta_query,
                    matched_utterance=matched_utterance,
                    matched_metta=matched_metta,
                    match_score=match_score,
                    queries=(
                        QueryExecution(
                            command_type=resolved_type,
                            original_input=user_query,
                            matched_metta=metta_query,
                            doc_ids=resolve_metta_doc_ids(metta_query, self.metta_docs),
                            original_responses=raw_result_output,
                            responses=_output_lines(formatted_output),
                        ),
                    ),
                )

            tick_query = f"!{SynchronizeTickFunctionPattern().to_metta()}"
            tick_output = self.metta.run(tick_query)
            raw_tick_output = collect_raw_metta_output(tick_output)
            formatted_tick_output = format_metta_output(tick_output)
            post_tick_state = end_state(self.metta)
            post_tick_event = post_tick_state[0] if post_tick_state else None
            post_tick_message = _decorate_end_state_message(
                post_tick_event,
                post_tick_state[1] if post_tick_state else None,
                self.move_count,
            )
            tick_responses = _append_unique_message(
                _output_lines(formatted_tick_output), post_tick_message
            )

            return CommandResult(
                ok=True,
                input_text=user_query,
                command_type=resolved_type,
                output=formatted_output,
                tick_output=formatted_tick_output,
                end_state_event=post_tick_event,
                end_state_message=post_tick_message,
                metta_query=metta_query,
                matched_utterance=matched_utterance,
                matched_metta=matched_metta,
                match_score=match_score,
                queries=(
                    QueryExecution(
                        command_type=resolved_type,
                        original_input=user_query,
                        matched_metta=metta_query,
                        doc_ids=resolve_metta_doc_ids(metta_query, self.metta_docs),
                        original_responses=raw_result_output,
                        responses=_output_lines(formatted_output),
                    ),
                    QueryExecution(
                        command_type="metta",
                        original_input=tick_query,
                        matched_metta=tick_query,
                        doc_ids=resolve_metta_doc_ids(tick_query, self.metta_docs),
                        original_responses=raw_tick_output,
                        responses=tick_responses,
                    ),
                ),
            )

    def _normalize_command_type(self, command_type: str, command: str) -> str:
        normalized = command_type.strip().lower()
        if normalized == "auto":
            stripped = command.strip()
            if stripped.startswith("!") or stripped.startswith("("):
                return "metta"
            return "natural_language"
        if normalized in {"natural_language", "natural-language", "nl"}:
            return "natural_language"
        if normalized == "metta":
            return "metta"
        raise ValueError(
            "Unsupported command_type. Expected one of: auto, natural_language, metta."
        )

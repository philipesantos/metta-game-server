import unittest
from unittest.mock import patch

from core.nlp.command_catalog import CommandEntry
from core.patterns.functions.synchronize_tick_function_pattern import (
    SynchronizeTickFunctionPattern,
)
from core.runtime import GameSession, MettaExecutionTimeoutError


class FakeWorld:
    def to_metta(self) -> str:
        return "WORLD"


class FakeEmbeddingIndex:
    next_match = None

    def __init__(self, entries, *args, **kwargs):
        self.entries = entries
        self.updated_entries = None

    def update_entries(self, entries):
        self.updated_entries = entries
        self.entries = entries

    def match(self, query):
        return self.__class__.next_match


class FakeAtom:
    def __init__(self, name: str):
        self.name = name

    def get_name(self):
        return self.name


class FakeMatchResult:
    def __init__(self, entry, score: float):
        self.entry = entry
        self.score = score


class FakeMetta:
    def __init__(
        self,
        *,
        win_message: str | None = None,
        game_over_message: str | None = None,
        responses: dict[str, object] | None = None,
        win_after_queries: set[str] | None = None,
        errors: dict[str, Exception] | None = None,
    ):
        self.win_message = win_message
        self.game_over_message = game_over_message
        self.responses = responses or {}
        self.win_after_queries = win_after_queries or set()
        self.errors = errors or {}
        self.calls: list[str] = []
        self._pending_win = False

    def run(self, query: str):
        self.calls.append(query)
        if "(GameWon $reason)" in query:
            if self.win_message is None:
                return [[]]
            if self.win_after_queries and not self._pending_win:
                return [[]]
            return [[FakeAtom(self.win_message)]]
        if "(GameOver $reason)" in query:
            if self.game_over_message is None:
                return [[]]
            return [[FakeAtom(self.game_over_message)]]
        if query in self.errors:
            raise self.errors[query]
        result = self.responses.get(query, [[]])
        if query in self.win_after_queries:
            self._pending_win = True
        return result


class TestGameSession(unittest.TestCase):
    def setUp(self):
        FakeEmbeddingIndex.next_match = None

    @patch("core.runtime.format_metta_output", side_effect=lambda output: str(output))
    @patch("core.runtime.build_command_catalog")
    def test_processes_natural_language_command(self, mock_catalog, _format_output):
        entry = CommandEntry(
            utterance="look around",
            intent="look",
            metta="look",
            slots={},
        )
        mock_catalog.return_value = [entry]
        FakeEmbeddingIndex.next_match = FakeMatchResult(entry=entry, score=0.91)
        sync_query = f"!{SynchronizeTickFunctionPattern().to_metta()}"
        metta = FakeMetta(
            responses={
                "WORLD": [[]],
                "!look": [["look-result"]],
                sync_query: [["tick-result"]],
            }
        )

        session = GameSession(
            metta_factory=lambda: metta,
            world_builder=lambda: FakeWorld(),
            embedding_index_cls=FakeEmbeddingIndex,
        )

        result = session.process_command("look around")

        self.assertTrue(result.ok)
        self.assertEqual(result.command_type, "natural_language")
        self.assertEqual(result.metta_query, "!look")
        self.assertEqual(result.matched_utterance, "look around")
        self.assertEqual(result.matched_metta, "look")
        self.assertEqual(result.match_score, 0.91)
        self.assertEqual(result.output, "[['look-result']]")
        self.assertEqual(result.tick_output, "[['tick-result']]")
        self.assertEqual(len(result.queries), 2)
        self.assertEqual(result.queries[0].command_type, "natural_language")
        self.assertEqual(result.queries[0].original_input, "look around")
        self.assertEqual(result.queries[0].matched_metta, "!look")
        self.assertEqual(result.queries[0].original_responses, ("look-result",))
        self.assertEqual(result.queries[0].responses, ("[['look-result']]",))
        self.assertEqual(result.queries[1].command_type, "metta")
        self.assertEqual(result.queries[1].original_input, sync_query)
        self.assertEqual(result.queries[1].matched_metta, sync_query)
        self.assertEqual(result.queries[1].original_responses, ("tick-result",))
        self.assertEqual(result.queries[1].responses, ("[['tick-result']]",))
        self.assertIsNone(result.end_state_event)
        self.assertIn("!look", metta.calls)
        self.assertIn(sync_query, metta.calls)
        self.assertEqual(mock_catalog.call_count, 1)

    @patch("core.runtime.format_metta_output", side_effect=lambda output: str(output))
    @patch("core.runtime.build_command_catalog", return_value=[])
    def test_processes_explicit_metta_command(self, _catalog, _format_output):
        sync_query = f"!{SynchronizeTickFunctionPattern().to_metta()}"
        metta = FakeMetta(
            responses={
                "WORLD": [[]],
                "!(move north)": [["move-result"]],
                sync_query: [["tick-result"]],
            }
        )

        session = GameSession(
            metta_factory=lambda: metta,
            world_builder=lambda: FakeWorld(),
            embedding_index_cls=FakeEmbeddingIndex,
        )

        result = session.process_command("!(move north)", command_type="metta")

        self.assertTrue(result.ok)
        self.assertEqual(result.command_type, "metta")
        self.assertEqual(result.metta_query, "!(move north)")
        self.assertEqual(result.output, "[['move-result']]")
        self.assertEqual(result.tick_output, "")
        self.assertEqual(result.queries[0].matched_metta, "!(move north)")
        self.assertEqual(result.queries[0].original_responses, ("move-result",))
        self.assertEqual(len(result.queries), 1)
        self.assertIsNone(result.end_state_event)
        self.assertIsNone(result.matched_metta)
        self.assertNotIn(sync_query, metta.calls)

    @patch("core.runtime.format_metta_output", side_effect=lambda output: str(output))
    @patch("core.runtime.build_command_catalog", return_value=[])
    def test_rejects_malformed_explicit_metta_without_advancing_game(
        self, _catalog, _format_output
    ):
        sync_query = f"!{SynchronizeTickFunctionPattern().to_metta()}"
        metta = FakeMetta(
            responses={
                "WORLD": [[]],
                "!(wait)": [["wait-result"]],
                sync_query: [["tick-result"]],
            },
            errors={"!(broken": RuntimeError("unexpected end of input")},
        )

        session = GameSession(
            metta_factory=lambda: metta,
            world_builder=lambda: FakeWorld(),
            embedding_index_cls=FakeEmbeddingIndex,
        )

        malformed = session.process_command("!(broken", command_type="metta")
        valid = session.process_command("!(wait)", command_type="metta")

        self.assertFalse(malformed.ok)
        self.assertEqual(
            malformed.error,
            "Malformed MeTTa command: unexpected end of input",
        )
        self.assertEqual(malformed.metta_query, "!(broken")
        self.assertEqual(len(malformed.queries), 1)
        self.assertEqual(malformed.queries[0].matched_metta, "!(broken")
        self.assertEqual(
            malformed.queries[0].original_responses,
            ("Malformed MeTTa command: unexpected end of input",),
        )
        self.assertEqual(malformed.queries[0].responses, ())
        self.assertEqual(session.move_count, 1)
        self.assertEqual(metta.calls.count(sync_query), 0)
        self.assertTrue(valid.ok)
        self.assertEqual(valid.output, "[['wait-result']]")

    @patch("core.runtime.format_metta_output", side_effect=lambda output: str(output))
    @patch("core.runtime.build_command_catalog", return_value=[])
    def test_rejects_explicit_metta_with_forbidden_tokens(
        self, _catalog, _format_output
    ):
        metta = FakeMetta(responses={"WORLD": [[]]})
        session = GameSession(
            metta_factory=lambda: metta,
            world_builder=lambda: FakeWorld(),
            embedding_index_cls=FakeEmbeddingIndex,
        )

        result = session.process_command(
            "!(bind! abs (py-atom math.fabs))",
            command_type="metta",
        )

        self.assertFalse(result.ok)
        self.assertEqual(
            result.error,
            "Explicit MeTTa command uses forbidden tokens: bind!, py-atom.",
        )
        self.assertEqual(result.metta_query, "!(bind! abs (py-atom math.fabs))")
        self.assertEqual(len(result.queries), 1)
        self.assertEqual(
            result.queries[0].original_responses,
            ("Explicit MeTTa command uses forbidden tokens: bind!, py-atom.",),
        )
        self.assertEqual(result.queries[0].responses, ())
        self.assertNotIn("!(bind! abs (py-atom math.fabs))", metta.calls)
        self.assertEqual(session.move_count, 0)

    @patch("core.runtime.format_metta_output", side_effect=lambda output: str(output))
    @patch("core.runtime.build_command_catalog", return_value=[])
    @patch(
        "core.runtime._run_metta_with_timeout",
        side_effect=MettaExecutionTimeoutError,
    )
    def test_times_out_explicit_metta_without_advancing_game(
        self, _run_with_timeout, _catalog, _format_output
    ):
        metta = FakeMetta(responses={"WORLD": [[]]})
        session = GameSession(
            metta_factory=lambda: metta,
            world_builder=lambda: FakeWorld(),
            embedding_index_cls=FakeEmbeddingIndex,
            explicit_metta_timeout_seconds=0.25,
        )

        result = session.process_command("!(wait)", command_type="metta")

        self.assertFalse(result.ok)
        self.assertEqual(
            result.error,
            "MeTTa command timed out after 0.25 seconds.",
        )
        self.assertEqual(result.metta_query, "!(wait)")
        self.assertEqual(
            result.queries[0].original_responses,
            ("MeTTa command timed out after 0.25 seconds.",),
        )
        self.assertEqual(result.queries[0].responses, ())
        self.assertNotIn("!(wait)", metta.calls)
        self.assertEqual(session.move_count, 0)

    @patch("core.runtime.format_metta_output", side_effect=lambda output: str(output))
    @patch("core.runtime.build_command_catalog", return_value=[])
    def test_does_not_execute_actions_after_game_is_won(self, _catalog, _format_output):
        metta = FakeMetta(win_message="You escaped.", responses={"WORLD": [[]]})

        session = GameSession(
            metta_factory=lambda: metta,
            world_builder=lambda: FakeWorld(),
            embedding_index_cls=FakeEmbeddingIndex,
        )

        result = session.process_command("use battery on plane")

        self.assertFalse(result.ok)
        self.assertEqual(result.end_state_event, "game_won")
        self.assertEqual(result.output, "You escaped.")
        self.assertEqual(result.error, "The game has already ended.")
        self.assertEqual(len(result.queries), 1)
        self.assertEqual(result.queries[0].matched_metta, None)
        self.assertEqual(result.queries[0].original_responses, ())
        self.assertEqual(result.queries[0].responses, ("You escaped.",))
        self.assertNotIn("!use (battery plane)", metta.calls)

    @patch("core.runtime.format_metta_output", side_effect=lambda output: str(output))
    @patch("core.runtime.build_command_catalog", return_value=[])
    def test_marks_game_over_when_tick_sync_ends_the_game(self, _catalog, _format_output):
        sync_query = f"!{SynchronizeTickFunctionPattern().to_metta()}"
        metta = FakeMetta(
            game_over_message="You died.",
            responses={
                "WORLD": [[]],
                "!look": [["look-result"]],
                sync_query: [["tick-result"]],
            },
        )

        with patch.object(
            FakeMetta,
            "run",
            side_effect=[
                [[]],  # WORLD
                [[]],  # startup
                [[]],  # startup GameWon
                [[]],  # startup GameOver
                [[]],  # pre-command GameWon
                [[]],  # pre-command GameOver
                [["look-result"]],  # !look
                [[]],  # post-command GameWon
                [[]],  # post-command GameOver
                [["tick-result"]],  # sync
                [[]],  # post-tick GameWon
                [[FakeAtom("You died.")]],  # post-tick GameOver
            ],
        ) as _:
            session = GameSession(
                metta_factory=lambda: metta,
                world_builder=lambda: FakeWorld(),
                embedding_index_cls=FakeEmbeddingIndex,
            )
            FakeEmbeddingIndex.next_match = FakeMatchResult(
                entry=CommandEntry(
                    utterance="look around",
                    intent="look",
                    metta="look",
                    slots={},
                ),
                score=0.91,
            )
            result = session.process_command("look around")

        self.assertEqual(result.end_state_event, "game_over")
        self.assertEqual(result.end_state_message, "You died.\nGame over in 1 move.")
        self.assertEqual(result.queries[1].original_responses, ("tick-result",))
        self.assertEqual(
            result.queries[1].responses,
            ("[['tick-result']]", "You died.\nGame over in 1 move."),
        )

    @patch("core.runtime.format_metta_output", side_effect=lambda output: str(output))
    @patch("core.runtime.build_command_catalog", return_value=[])
    def test_rejects_unknown_command_type(self, _catalog, _format_output):
        session = GameSession(
            metta_factory=lambda: FakeMetta(responses={"WORLD": [[]]}),
            world_builder=lambda: FakeWorld(),
            embedding_index_cls=FakeEmbeddingIndex,
        )

        with self.assertRaises(ValueError):
            session.process_command("look around", command_type="voice")

    @patch("core.runtime.format_metta_output", side_effect=lambda output: str(output))
    @patch("core.runtime.build_command_catalog")
    def test_appends_move_count_to_win_message(self, mock_catalog, _format_output):
        entry = CommandEntry(
            utterance="look around",
            intent="look",
            metta="look",
            slots={},
        )
        mock_catalog.return_value = [entry]
        FakeEmbeddingIndex.next_match = FakeMatchResult(entry=entry, score=0.91)
        sync_query = f"!{SynchronizeTickFunctionPattern().to_metta()}"
        metta = FakeMetta(
            win_message="You escaped.",
            responses={
                "WORLD": [[]],
                "!(wait)": [["wait-result"]],
                "!look": [["look-result"]],
                sync_query: [["tick-result"]],
            },
            win_after_queries={"!look"},
        )

        session = GameSession(
            metta_factory=lambda: metta,
            world_builder=lambda: FakeWorld(),
            embedding_index_cls=FakeEmbeddingIndex,
        )

        first = session.process_command("!(wait)", command_type="metta")
        second = session.process_command("look around")

        self.assertIsNone(first.end_state_event)
        self.assertEqual(second.end_state_event, "game_won")
        self.assertEqual(second.end_state_message, "You escaped.\nYou won in 2 moves.")
        self.assertEqual(
            second.queries[0].responses,
            ("[['look-result']]", "You escaped.\nYou won in 2 moves."),
        )

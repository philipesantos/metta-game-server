from hyperon import MeTTa
from core.nlp import EmbeddingIndex, build_command_catalog
from core.patterns.events.startup_event_pattern import StartupEventPattern
from core.patterns.facts.game_over_fact_pattern import GameOverFactPattern
from core.patterns.facts.game_won_fact_pattern import GameWonFactPattern
from core.patterns.functions.synchronize_tick_function_pattern import (
    SynchronizeTickFunctionPattern,
)
from core.patterns.functions.trigger_function_pattern import TriggerFunctionPattern
from core.patterns.wrappers.state_wrapper_pattern import StateWrapperPattern
from core.world_builder import build_world
from utils.response import format_metta_output


def _unwrap_atom(atom) -> str:
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


def _end_state_message(metta: MeTTa) -> str | None:
    for pattern in (
        GameWonFactPattern("$reason"),
        GameOverFactPattern("$reason"),
    ):
        result = metta.run(
            f"!(match &self {StateWrapperPattern(pattern).to_metta()} $reason)"
        )
        if result and result[0]:
            return _unwrap_atom(result[0][0])
    return None


def main():
    metta = MeTTa()
    world = build_world()
    metta_code = world.to_metta()
    print(metta_code)
    print(metta.run(metta_code))
    command_catalog = build_command_catalog(world, metta)
    embedding_index = EmbeddingIndex(
        command_catalog,
        model_name="BAAI/bge-small-en-v1.5",
        min_score=0.55,
        min_margin=0.06,
        high_confidence_score=0.82,
    )

    startup_output = metta.run(
        f"!{TriggerFunctionPattern(StartupEventPattern()).to_metta()}"
    )
    print(f"\n--- Command Catalog ({len(command_catalog)}) ---")
    for entry in command_catalog:
        print(f"{entry.utterance} -> {entry.metta}")
    print(format_metta_output(startup_output))

    print("\n--- MeTTa Console ---")
    print("Type 'exit' to quit.")

    while True:
        user_query = input(">> ")

        if user_query.strip().lower() in ("exit", "quit"):
            break

        stripped = user_query.strip()
        end_state_message = _end_state_message(metta)
        if end_state_message is not None:
            print(end_state_message)
            continue

        if stripped.startswith("!") or stripped.startswith("("):
            metta_query = stripped
        else:
            command_catalog = build_command_catalog(world, metta)
            embedding_index.update_entries(command_catalog)
            match = embedding_index.match(stripped)
            if match is None:
                print("That doesn't seem possible right now.")
                continue
            print(f"[NL] {stripped} -> {match.entry.metta} ({match.score:.3f})")
            metta_query = f"!{match.entry.metta}"

        result_output = metta.run(metta_query)
        end_state_message = _end_state_message(metta)
        if end_state_message is not None:
            print(end_state_message)
            continue
        print(format_metta_output(result_output))
        print(metta.run(f"!{SynchronizeTickFunctionPattern().to_metta()}"))


if __name__ == "__main__":
    main()

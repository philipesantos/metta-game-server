import asyncio
import os

from core.runtime import GameSession, end_state_message
from core.websocket_input import run_websocket_server

INPUT_MODE_ENV_VAR = "METTA_RIFT_INPUT_MODE"
WEBSOCKET_HOST_ENV_VAR = "METTA_RIFT_WEBSOCKET_HOST"
WEBSOCKET_PORT_ENV_VAR = "METTA_RIFT_WEBSOCKET_PORT"


def _end_state_message(metta) -> str | None:
    return end_state_message(metta)


def _input_mode() -> str:
    mode = os.getenv(INPUT_MODE_ENV_VAR, "cli").strip().lower()
    if mode not in {"cli", "websocket"}:
        raise ValueError(
            f"{INPUT_MODE_ENV_VAR} must be either 'cli' or 'websocket', got '{mode}'."
        )
    return mode


def _websocket_host() -> str:
    return os.getenv(WEBSOCKET_HOST_ENV_VAR, "127.0.0.1").strip() or "127.0.0.1"


def _websocket_port() -> int:
    raw_port = os.getenv(WEBSOCKET_PORT_ENV_VAR, "8765").strip()
    try:
        return int(raw_port)
    except ValueError as exc:
        raise ValueError(
            f"{WEBSOCKET_PORT_ENV_VAR} must be a valid integer, got '{raw_port}'."
        ) from exc


def _print_startup(session: GameSession) -> None:
    print(session.metta_code)
    print(session.world_load_output)
    print(f"\n--- Command Catalog ({len(session.command_catalog)}) ---")
    for entry in session.command_catalog:
        print(f"{entry.utterance} -> {entry.metta}")
    print(session.startup_output)


def _print_command_result(result) -> None:
    if result.command_type == "natural_language" and result.matched_metta:
        print(
            f"[NL] {result.input_text.strip()} -> {result.matched_metta} ({result.match_score:.3f})"
        )

    if result.output:
        print(result.output)
    elif result.error:
        print(result.error)

    if result.tick_output:
        print(result.tick_output)


def _run_cli(session: GameSession) -> None:
    print("\n--- MeTTa Console ---")
    print("Type 'exit' to quit.")

    while True:
        user_query = input(">> ")
        if user_query.strip().lower() in ("exit", "quit"):
            break
        result = session.process_command(user_query)
        _print_command_result(result)


def _run_websocket(session: GameSession) -> None:
    host = _websocket_host()
    port = _websocket_port()
    print("\n--- Websocket Input ---")
    print(f"Listening on ws://{host}:{port}")
    asyncio.run(run_websocket_server(session, host=host, port=port))


def main():
    session = GameSession()
    _print_startup(session)

    if _input_mode() == "websocket":
        _run_websocket(session)
        return

    _run_cli(session)


if __name__ == "__main__":
    main()

import asyncio
import os

from core.runtime import GameSession, end_state_message
from core.websocket_input import run_websocket_server

INPUT_MODE_ENV_VAR = "METTA_GAME_INPUT_MODE"
LEGACY_INPUT_MODE_ENV_VAR = "METTA_RIFT_INPUT_MODE"
WEBSOCKET_HOST_ENV_VAR = "METTA_GAME_WEBSOCKET_HOST"
LEGACY_WEBSOCKET_HOST_ENV_VAR = "METTA_RIFT_WEBSOCKET_HOST"
WEBSOCKET_PORT_ENV_VAR = "METTA_GAME_WEBSOCKET_PORT"
LEGACY_WEBSOCKET_PORT_ENV_VAR = "METTA_RIFT_WEBSOCKET_PORT"


def _end_state_message(metta) -> str | None:
    return end_state_message(metta)


def _getenv(primary: str, legacy: str, default: str) -> str:
    value = os.getenv(primary)
    if value is not None:
        return value
    return os.getenv(legacy, default)


def _input_mode() -> str:
    mode = _getenv(INPUT_MODE_ENV_VAR, LEGACY_INPUT_MODE_ENV_VAR, "websocket")
    mode = mode.strip().lower()
    if mode not in {"cli", "websocket"}:
        raise ValueError(
            f"{INPUT_MODE_ENV_VAR} must be either 'cli' or 'websocket', got '{mode}'."
        )
    return mode


def _websocket_host() -> str:
    host = _getenv(
        WEBSOCKET_HOST_ENV_VAR, LEGACY_WEBSOCKET_HOST_ENV_VAR, "127.0.0.1"
    )
    return host.strip() or "127.0.0.1"


def _websocket_port() -> int:
    raw_port = _getenv(WEBSOCKET_PORT_ENV_VAR, LEGACY_WEBSOCKET_PORT_ENV_VAR, "8765")
    raw_port = raw_port.strip()
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
    elif result.command_type == "metta" and result.queries:
        raw_values = result.queries[0].original_responses
        if raw_values:
            for raw_value in raw_values:
                print(raw_value)
    elif result.error:
        print(result.error)

    if result.tick_output:
        print(result.tick_output)


def _run_cli(session: GameSession) -> None:
    print("\n--- MeTTa Game Console ---")
    print("Type 'exit' to quit.")

    while True:
        user_query = input(">> ")
        if user_query.strip().lower() in ("exit", "quit"):
            break
        result = session.process_command(user_query)
        _print_command_result(result)


def _run_websocket() -> None:
    host = _websocket_host()
    port = _websocket_port()
    print("\n--- Websocket Input ---")
    print(f"Listening on ws://{host}:{port}")
    try:
        asyncio.run(run_websocket_server(host=host, port=port))
    except KeyboardInterrupt:
        return


def main():
    if _input_mode() == "websocket":
        _run_websocket()
        return

    session = GameSession()
    session.refresh_command_catalog()
    _print_startup(session)
    _run_cli(session)


if __name__ == "__main__":
    main()

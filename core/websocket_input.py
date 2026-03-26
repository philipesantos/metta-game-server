import asyncio
import json
from http import HTTPStatus
from json import JSONDecodeError
from typing import Callable
from uuid import UUID

from core.runtime import CommandResult, GameSession


class InvalidWebSocketMessage(ValueError):
    pass


HEALTHCHECK_PATH = "/healthz"


def _parse_message_uuid(payload: dict) -> str:
    message_uuid = payload.get("uuid")
    if not isinstance(message_uuid, str):
        raise InvalidWebSocketMessage("The uuid field must be a string.")
    try:
        return str(UUID(message_uuid))
    except ValueError as exc:
        raise InvalidWebSocketMessage(
            "The uuid field must be a valid UUID string."
        ) from exc


def parse_websocket_message(message: str) -> tuple[str, str, str]:
    try:
        payload = json.loads(message)
    except JSONDecodeError as exc:
        raise InvalidWebSocketMessage(
            "Websocket messages must be valid JSON objects."
        ) from exc

    if not isinstance(payload, dict):
        raise InvalidWebSocketMessage(
            "Websocket messages must be JSON objects with a command field."
        )

    command = payload.get("command")
    if not isinstance(command, str):
        raise InvalidWebSocketMessage("The command field must be a string.")

    command_type = payload.get("command_type")
    if not isinstance(command_type, str):
        raise InvalidWebSocketMessage("The command_type field must be a string.")
    normalized_command_type = command_type.strip().lower()
    if normalized_command_type not in {"natural_language", "metta"}:
        raise InvalidWebSocketMessage(
            "The command_type field must be either 'natural_language' or 'metta'."
        )

    return command, normalized_command_type, _parse_message_uuid(payload)


def serialize_command_result(result: CommandResult, message_uuid: str | None = None) -> str:
    payload = {
        "event": "command_result",
        "queries": [
            {
                "command_type": query_execution.command_type,
                "original_input": query_execution.original_input,
                "matched_metta": query_execution.matched_metta,
                "original_responses": list(query_execution.original_responses),
                "responses": list(query_execution.responses),
            }
            for query_execution in result.queries
        ],
    }
    if message_uuid is not None:
        payload["uuid"] = message_uuid
    return json.dumps(payload)


def serialize_startup_event(metta_code: str) -> str:
    return json.dumps(
        {
            "event": "startup",
            "metta_code": metta_code,
        }
    )


def serialize_terminal_event(event_name: str, message_uuid: str | None = None) -> str:
    payload = {
        "event": event_name,
    }
    if message_uuid is not None:
        payload["uuid"] = message_uuid
    return json.dumps(payload)


def serialize_error_event(error: str, message_uuid: str | None = None) -> str:
    payload = {
        "event": "error",
        "error": error,
    }
    if message_uuid is not None:
        payload["uuid"] = message_uuid
    return json.dumps(payload)


def _normalize_request_path(path: str) -> str:
    return path.split("?", 1)[0]


def process_healthcheck_request(*args):
    if len(args) != 2:
        raise TypeError("process_healthcheck_request expects exactly two arguments.")

    first, second = args

    # websockets <= 10 passes (path, headers)
    if isinstance(first, str):
        if _normalize_request_path(first) != HEALTHCHECK_PATH:
            return None
        return (
            HTTPStatus.OK,
            [
                ("Content-Type", "text/plain; charset=utf-8"),
                ("Content-Length", "3"),
            ],
            b"OK\n",
        )

    # websockets >= 13 passes (connection, request)
    request_path = getattr(second, "path", "")
    if _normalize_request_path(request_path) != HEALTHCHECK_PATH:
        return None

    return first.respond(HTTPStatus.OK, "OK\n")


async def run_websocket_server(
    session_factory: Callable[[], GameSession] = GameSession,
    *,
    host: str = "127.0.0.1",
    port: int = 8765,
) -> None:
    try:
        import websockets
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Websocket mode requires the 'websockets' package to be installed."
        ) from exc

    async def handle_connection(websocket):
        session = session_factory()
        await websocket.send(serialize_startup_event(session.metta_code))
        if session.startup_result.queries and session.startup_result.queries[0].responses:
            await websocket.send(serialize_command_result(session.startup_result))
        if session.startup_result.end_state_event and session.startup_result.end_state_message:
            await websocket.send(
                serialize_terminal_event(session.startup_result.end_state_event)
            )

        async for message in websocket:
            message_uuid = None
            try:
                command, command_type, message_uuid = parse_websocket_message(message)
                result = session.process_command(command, command_type=command_type)
                response = serialize_command_result(result, message_uuid)
                terminal_response = None
                if result.end_state_event and result.end_state_message:
                    terminal_response = serialize_terminal_event(
                        result.end_state_event, message_uuid
                    )
            except (InvalidWebSocketMessage, ValueError) as exc:
                response = serialize_error_event(str(exc), message_uuid)
                terminal_response = None
            await websocket.send(response)
            if terminal_response is not None:
                await websocket.send(terminal_response)

    async with websockets.serve(
        handle_connection,
        host,
        port,
        process_request=process_healthcheck_request,
    ):
        await asyncio.Future()

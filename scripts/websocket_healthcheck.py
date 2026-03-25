import os
import socket
import sys

WEBSOCKET_PORT_ENV_VAR = "METTA_GAME_WEBSOCKET_PORT"
LEGACY_WEBSOCKET_PORT_ENV_VAR = "METTA_RIFT_WEBSOCKET_PORT"

_HANDSHAKE_TEMPLATE = (
    "GET / HTTP/1.1\r\n"
    "Host: {host}:{port}\r\n"
    "Upgrade: websocket\r\n"
    "Connection: Upgrade\r\n"
    "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\n"
    "Sec-WebSocket-Version: 13\r\n"
    "\r\n"
)


def websocket_port_from_env(environ: dict[str, str] | None = None) -> int:
    environ = os.environ if environ is None else environ
    raw_port = (
        environ.get(WEBSOCKET_PORT_ENV_VAR)
        or environ.get(LEGACY_WEBSOCKET_PORT_ENV_VAR)
        or "8765"
    )
    return int(raw_port)


def probe_websocket(host: str = "127.0.0.1", port: int = 8765, timeout: float = 2.0) -> None:
    request = _HANDSHAKE_TEMPLATE.format(host=host, port=port).encode("ascii")
    with socket.create_connection((host, port), timeout=timeout) as connection:
        connection.settimeout(timeout)
        connection.sendall(request)
        response = connection.recv(4096).decode("ascii", errors="replace")

    status_line = response.split("\r\n", 1)[0]
    if not status_line.startswith(("HTTP/1.1 101 ", "HTTP/1.0 101 ")):
        raise RuntimeError(f"Expected websocket upgrade response, got: {status_line!r}")

    normalized_response = response.lower()
    if "upgrade: websocket" not in normalized_response:
        raise RuntimeError("Websocket upgrade response is missing the Upgrade header.")
    if "connection: upgrade" not in normalized_response:
        raise RuntimeError("Websocket upgrade response is missing the Connection header.")


def main() -> int:
    try:
        probe_websocket(port=websocket_port_from_env())
    except Exception:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

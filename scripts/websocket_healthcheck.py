import os
import socket

WEBSOCKET_PORT_ENV_VAR = "METTA_GAME_WEBSOCKET_PORT"
LEGACY_WEBSOCKET_PORT_ENV_VAR = "METTA_RIFT_WEBSOCKET_PORT"
HEALTHCHECK_PATH = "/healthz"

_REQUEST_TEMPLATE = (
    "GET {path} HTTP/1.1\r\n"
    "Host: {host}:{port}\r\n"
    "Connection: close\r\n"
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
    request = _REQUEST_TEMPLATE.format(
        path=HEALTHCHECK_PATH,
        host=host,
        port=port,
    ).encode("ascii")
    with socket.create_connection((host, port), timeout=timeout) as connection:
        connection.settimeout(timeout)
        connection.sendall(request)
        response = connection.recv(4096).decode("ascii", errors="replace")

    status_line = response.split("\r\n", 1)[0]
    if not status_line.startswith(("HTTP/1.1 200 ", "HTTP/1.0 200 ")):
        raise RuntimeError(f"Expected healthcheck OK response, got: {status_line!r}")


def main() -> int:
    try:
        probe_websocket(port=websocket_port_from_env())
    except Exception:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

import unittest
from unittest.mock import patch

from core.websocket_input import HEALTHCHECK_PATH
from scripts.websocket_healthcheck import probe_websocket, websocket_port_from_env


class FakeSocket:
    def __init__(self, response: bytes):
        self.response = response
        self.timeout = None
        self.sent = b""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def settimeout(self, timeout):
        self.timeout = timeout

    def sendall(self, data: bytes):
        self.sent += data

    def recv(self, size: int) -> bytes:
        return self.response


class TestWebsocketHealthcheck(unittest.TestCase):
    def test_websocket_port_from_env_prefers_primary_name(self):
        port = websocket_port_from_env(
            {
                "METTA_GAME_WEBSOCKET_PORT": "9001",
                "METTA_RIFT_WEBSOCKET_PORT": "9000",
            }
        )

        self.assertEqual(port, 9001)

    def test_websocket_port_from_env_uses_legacy_name(self):
        port = websocket_port_from_env({"METTA_RIFT_WEBSOCKET_PORT": "9000"})

        self.assertEqual(port, 9000)

    def test_probe_websocket_requests_health_endpoint(self):
        fake_socket = FakeSocket(
            b"HTTP/1.1 200 OK\r\n"
            b"Content-Length: 3\r\n"
            b"\r\n"
            b"OK\n"
        )

        with patch(
            "scripts.websocket_healthcheck.socket.create_connection",
            return_value=fake_socket,
        ) as mock_create_connection:
            probe_websocket(host="localhost", port=8765, timeout=1.5)

        mock_create_connection.assert_called_once_with(("localhost", 8765), timeout=1.5)
        self.assertEqual(fake_socket.timeout, 1.5)
        self.assertIn(f"GET {HEALTHCHECK_PATH} HTTP/1.1\r\n".encode(), fake_socket.sent)
        self.assertIn(b"Connection: close\r\n", fake_socket.sent)

    def test_probe_websocket_accepts_ok_response(self):
        fake_socket = FakeSocket(
            b"HTTP/1.1 200 OK\r\n"
            b"Content-Length: 2\r\n"
            b"\r\n"
            b"ok"
        )

        with patch(
            "scripts.websocket_healthcheck.socket.create_connection",
            return_value=fake_socket,
        ):
            probe_websocket()

    def test_probe_websocket_rejects_non_healthcheck_response(self):
        fake_socket = FakeSocket(
            b"HTTP/1.1 503 Service Unavailable\r\n"
            b"Content-Length: 2\r\n"
            b"\r\n"
            b"no"
        )

        with patch(
            "scripts.websocket_healthcheck.socket.create_connection",
            return_value=fake_socket,
        ):
            with self.assertRaises(RuntimeError):
                probe_websocket()


if __name__ == "__main__":
    unittest.main()

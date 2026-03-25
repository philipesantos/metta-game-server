import unittest
from unittest.mock import Mock, patch

import main


class FakeAtom:
    def __init__(self, name: str):
        self.name = name

    def get_name(self):
        return self.name


class FakeSession:
    metta_code = "WORLD"
    world_load_output = [[]]
    command_catalog = []
    startup_output = ""
    startup_result = None


class FakeMetta:
    def __init__(
        self, win_message: str | None = None, game_over_message: str | None = None
    ):
        self.win_message = win_message
        self.game_over_message = game_over_message
        self.calls: list[str] = []

    def run(self, query: str):
        self.calls.append(query)
        if "(GameWon $reason)" in query:
            if self.win_message is None:
                return [[]]
            return [[FakeAtom(self.win_message)]]
        if "(GameOver $reason)" in query:
            if self.game_over_message is None:
                return [[]]
            return [[FakeAtom(self.game_over_message)]]
        return [[]]


class TestMain(unittest.TestCase):
    def test_end_state_message_returns_game_won_before_game_over(self):
        metta = FakeMetta(
            win_message="You escaped.",
            game_over_message="You died.",
        )

        result = main._end_state_message(metta)

        self.assertEqual(result, "You escaped.")
        self.assertEqual(len(metta.calls), 1)
        self.assertIn("(GameWon $reason)", metta.calls[0])

    def test_end_state_message_returns_game_over_when_no_win_exists(self):
        metta = FakeMetta(game_over_message="You died.")

        result = main._end_state_message(metta)

        self.assertEqual(result, "You died.")
        self.assertEqual(len(metta.calls), 2)
        self.assertIn("(GameWon $reason)", metta.calls[0])
        self.assertIn("(GameOver $reason)", metta.calls[1])

    @patch.dict("os.environ", {}, clear=True)
    def test_input_mode_defaults_to_websocket(self):
        self.assertEqual(main._input_mode(), "websocket")

    @patch.dict("os.environ", {main.INPUT_MODE_ENV_VAR: "websocket"})
    def test_input_mode_reads_websocket_env(self):
        self.assertEqual(main._input_mode(), "websocket")

    @patch.dict("os.environ", {main.LEGACY_INPUT_MODE_ENV_VAR: "cli"}, clear=True)
    def test_input_mode_reads_legacy_env_when_new_name_is_unset(self):
        self.assertEqual(main._input_mode(), "cli")

    @patch.dict("os.environ", {main.INPUT_MODE_ENV_VAR: "cli"})
    @patch("main._run_cli")
    @patch("main._run_websocket")
    @patch("main._print_startup")
    def test_main_runs_cli_mode(self, mock_print_startup, mock_run_websocket, mock_run_cli):
        session = FakeSession()

        with patch("main.GameSession", return_value=session):
            main.main()

        mock_print_startup.assert_called_once_with(session)
        mock_run_cli.assert_called_once_with(session)
        mock_run_websocket.assert_not_called()

    @patch.dict("os.environ", {main.INPUT_MODE_ENV_VAR: "websocket"})
    @patch("main._run_cli")
    @patch("main._run_websocket")
    @patch("main._print_startup")
    def test_main_runs_websocket_mode(
        self, mock_print_startup, mock_run_websocket, mock_run_cli
    ):
        with patch("main.GameSession") as mock_session:
            main.main()

        mock_session.assert_not_called()
        mock_print_startup.assert_not_called()
        mock_run_websocket.assert_called_once_with()
        mock_run_cli.assert_not_called()

    @patch("main.asyncio.run", side_effect=KeyboardInterrupt)
    @patch("main.run_websocket_server", new_callable=Mock, return_value="server")
    def test_run_websocket_exits_cleanly_on_keyboard_interrupt(
        self, mock_run_websocket_server, mock_asyncio_run
    ):
        main._run_websocket()

        mock_run_websocket_server.assert_called_once_with(host="127.0.0.1", port=8765)
        mock_asyncio_run.assert_called_once()

    @patch.dict("os.environ", {main.LEGACY_WEBSOCKET_HOST_ENV_VAR: "0.0.0.0"}, clear=True)
    def test_websocket_host_reads_legacy_env_when_new_name_is_unset(self):
        self.assertEqual(main._websocket_host(), "0.0.0.0")

    @patch.dict("os.environ", {main.LEGACY_WEBSOCKET_PORT_ENV_VAR: "9000"}, clear=True)
    def test_websocket_port_reads_legacy_env_when_new_name_is_unset(self):
        self.assertEqual(main._websocket_port(), 9000)


if __name__ == "__main__":
    unittest.main()

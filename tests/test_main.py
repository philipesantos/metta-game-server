import unittest
from unittest.mock import patch

import main


class FakeAtom:
    def __init__(self, name: str):
        self.name = name

    def get_name(self):
        return self.name


class FakeWorld:
    def to_metta(self) -> str:
        return "WORLD"


class FakeEmbeddingIndex:
    def __init__(self, *args, **kwargs):
        pass

    def update_entries(self, entries):
        pass

    def match(self, query):
        return None


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

    @patch("builtins.input", side_effect=["use battery on plane", "exit"])
    @patch("builtins.print")
    @patch("main.format_metta_output", return_value="")
    @patch("main.EmbeddingIndex", FakeEmbeddingIndex)
    @patch("main.build_command_catalog", return_value=[])
    @patch("main.build_world", return_value=FakeWorld())
    def test_main_does_not_execute_actions_after_game_is_won(
        self,
        _build_world,
        _build_command_catalog,
        _format_metta_output,
        mock_print,
        _input,
    ):
        metta = FakeMetta(win_message="You escaped.")

        with patch("main.MeTTa", return_value=metta):
            main.main()

        self.assertIn(
            "You escaped.", [call.args[0] for call in mock_print.call_args_list]
        )
        self.assertNotIn("!use (battery plane)", metta.calls)
        self.assertFalse(
            any(
                "[NL] use battery on plane" in str(call.args[0])
                for call in mock_print.call_args_list
            )
        )


if __name__ == "__main__":
    unittest.main()

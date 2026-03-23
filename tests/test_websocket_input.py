import unittest

from core.runtime import CommandResult, QueryExecution
from core.websocket_input import (
    InvalidWebSocketMessage,
    parse_websocket_message,
    serialize_command_result,
    serialize_startup_event,
    serialize_terminal_event,
)


class TestWebSocketInput(unittest.TestCase):
    def test_parse_websocket_message_accepts_json_object(self):
        command, command_type = parse_websocket_message(
            '{"command": "look around", "command_type": "natural_language"}'
        )

        self.assertEqual(command, "look around")
        self.assertEqual(command_type, "natural_language")

    def test_parse_websocket_message_accepts_metta_command_type(self):
        command, command_type = parse_websocket_message(
            '{"command": "!(move north)", "command_type": "metta"}'
        )

        self.assertEqual(command, "!(move north)")
        self.assertEqual(command_type, "metta")

    def test_parse_websocket_message_rejects_missing_command_type(self):
        with self.assertRaises(InvalidWebSocketMessage):
            parse_websocket_message('{"command": "!(move north)"}')

    def test_parse_websocket_message_rejects_invalid_command_type(self):
        with self.assertRaises(InvalidWebSocketMessage):
            parse_websocket_message(
                '{"command": "look around", "command_type": "auto"}'
            )

    def test_parse_websocket_message_rejects_non_json(self):
        with self.assertRaises(InvalidWebSocketMessage):
            parse_websocket_message("look around")

    def test_parse_websocket_message_rejects_non_object_payload(self):
        with self.assertRaises(InvalidWebSocketMessage):
            parse_websocket_message('["look around"]')

    def test_serialize_command_result_emits_json(self):
        payload = serialize_command_result(
            CommandResult(
                ok=True,
                input_text="look around",
                command_type="natural_language",
                output="You are in a cabin.",
                tick_output="",
                metta_query="!look",
                matched_utterance="look around",
                matched_metta="look",
                match_score=0.91,
                queries=(
                    QueryExecution(
                        command_type="natural_language",
                        original_input="look around",
                        matched_metta="!look",
                        original_responses=("(Response 5 \"You are in a cabin.\")",),
                        responses=("You are in a cabin.",),
                    ),
                    QueryExecution(
                        command_type="metta",
                        original_input="!sync",
                        matched_metta="!sync",
                        original_responses=(),
                        responses=(),
                    ),
                ),
            )
        )

        self.assertIn('"event": "command_result"', payload)
        self.assertIn('"command_type": "natural_language"', payload)
        self.assertIn('"original_input": "look around"', payload)
        self.assertIn('"matched_metta": "!look"', payload)
        self.assertIn('"original_responses": ["(Response 5 \\"You are in a cabin.\\")"]', payload)
        self.assertIn('"responses": ["You are in a cabin."]', payload)
        self.assertIn('"command_type": "metta"', payload)
        self.assertIn('"original_input": "!sync"', payload)

    def test_serialize_startup_event_has_no_messages(self):
        payload = serialize_startup_event("(= (look) Empty)")

        self.assertIn('"event": "startup"', payload)
        self.assertIn('"metta_code": "(= (look) Empty)"', payload)
        self.assertNotIn('command_schema', payload)
        self.assertNotIn('startup_output', payload)

    def test_serialize_command_result_can_represent_startup_messages(self):
        payload = serialize_command_result(
            CommandResult(
                ok=True,
                input_text="!(trigger (Startup))",
                command_type="metta",
                queries=(
                    QueryExecution(
                        command_type="metta",
                        original_input="!(trigger (Startup))",
                        matched_metta="!(trigger (Startup))",
                        original_responses=("(Response 100 \"Welcome to the cabin.\")",),
                        responses=("Welcome to the cabin.",),
                    ),
                ),
            )
        )

        self.assertIn('"event": "command_result"', payload)
        self.assertIn('"original_input": "!(trigger (Startup))"', payload)
        self.assertIn('"original_responses": ["(Response 100 \\"Welcome to the cabin.\\")"]', payload)
        self.assertIn('"responses": ["Welcome to the cabin."]', payload)

    def test_serialize_terminal_event_emits_game_event_json(self):
        payload = serialize_terminal_event("game_won")

        self.assertIn('"event": "game_won"', payload)
        self.assertNotIn('"message"', payload)

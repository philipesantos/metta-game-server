import unittest

from core.definitions.facts.character_fact_definition import CharacterFactDefinition
from core.patterns.facts.character_fact_pattern import CharacterFactPattern
from tests.utils.metta import get_test_metta

from tests.utils.utils import unwrap_first_match
from utils.type import Type


class TestCharacterFactDefinition(unittest.TestCase):
    def test_to_metta(self):
        metta = get_test_metta()

        key = "player"
        name = "John"

        metta.run(CharacterFactDefinition(key, name).to_metta())

        result_type = metta.run(f"!(get-type {key})")
        self.assertEqual(unwrap_first_match(result_type), Type.CHARACTER.value)

        character_key = CharacterFactPattern("$key", name)
        result_key = metta.run(f"!(match &self {character_key.to_metta()} $key)")
        self.assertEqual(unwrap_first_match(result_key), key)

        character_name = CharacterFactPattern(key, "$name")
        result_name = metta.run(f"!(match &self {character_name.to_metta()} $name)")
        self.assertEqual(unwrap_first_match(result_name), name)

        character_no_match = CharacterFactPattern("james", name)
        result_no_match = metta.run(
            f"!(match &self {character_no_match.to_metta()} True)"
        )
        self.assertEqual(result_no_match, [[]])

    def test_includes_enter_text_when_provided(self):
        metta = get_test_metta()

        metta.run(
            CharacterFactDefinition(
                "bear",
                "Bear",
                text_enter="A bear is here.",
                enter_priority=30,
            ).to_metta()
        )

        result_text = metta.run('!(match &self (EnterText bear $text) $text)')
        self.assertEqual(unwrap_first_match(result_text), "A bear is here.")

        result_priority = metta.run("!(match &self (EnterPriority bear $priority) $priority)")
        self.assertEqual(unwrap_first_match(result_priority), 30)


if __name__ == "__main__":
    unittest.main()

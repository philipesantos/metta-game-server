import unittest

from core.patterns.facts.character_fact_pattern import CharacterFactPattern
from modules.statues.functions.statues_helpers_function_definition import (
    StatuesHelpersFunctionDefinition,
)
from modules.statues.side_effects.statues_module_on_use_rune_on_statue import (
    StatuesModuleOnUseRuneOnStatue,
)


class TestStatuesGeneratedMetta(unittest.TestCase):
    def test_helpers_definition_exposes_shared_predicates(self):
        metta = StatuesHelpersFunctionDefinition().to_metta()

        self.assertIn("(= (statue-has-any-rune ($statue))", metta)
        self.assertIn("(= (all-statues-filled)", metta)
        self.assertIn("(= (statues-solved)", metta)
        self.assertIn("(= (statue-filled-message ($statue $statue_name))", metta)

    def test_rune_use_trigger_calls_shared_helpers(self):
        side_effect = StatuesModuleOnUseRuneOnStatue(
            CharacterFactPattern("player", "John"),
            "omicron_rune",
            "omicron rune",
            "lion_statue",
            "lion statue",
        )

        metta = side_effect.to_metta(None)

        self.assertIn("(statue-has-any-rune (lion_statue))", metta)
        self.assertIn('(statue-filled-message (lion_statue "lion statue"))', metta)
        self.assertIn("(statues-solved)", metta)
        self.assertIn("(all-statues-filled)", metta)
        self.assertNotIn("(exists (State (At epsilon_rune lion_statue)))", metta)


if __name__ == "__main__":
    unittest.main()

import unittest

from core.definitions.functions.inventory_function_definition import (
    InventoryFunctionPattern as InventoryFunctionDefinition,
)
from core.definitions.facts.item_fact_definition import ItemFactDefinition
from core.definitions.wrappers.state_wrapper_definition import StateWrapperDefinition
from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.patterns.facts.character_fact_pattern import CharacterFactPattern
from core.patterns.functions.inventory_function_pattern import (
    InventoryFunctionPattern,
)
from tests.utils.metta import get_test_metta
from utils.response import format_metta_output


class TestInventoryFunctionDefinition(unittest.TestCase):
    def test_to_metta(self):
        metta = get_test_metta()

        character = CharacterFactPattern("player", "John")

        metta.run(InventoryFunctionDefinition(character).to_metta())

        inventory = InventoryFunctionPattern()
        result_empty = metta.run(f"!{inventory.to_metta()}")
        self.assertEqual(format_metta_output(result_empty), "Your inventory is empty.")

        metta.run(
            ItemFactDefinition(
                "sword",
                "picked",
                "dropped",
                "examined",
                name="Worn sword",
                text_look="A worn sword hangs from your belt.",
            ).to_metta()
        )
        metta.run(
            ItemFactDefinition(
                "apple",
                "picked",
                "dropped",
                "examined",
                name="Red apple",
                text_look="A red apple sits in your pouch.",
            ).to_metta()
        )

        metta.run(
            StateWrapperDefinition(AtFactPattern("sword", character.key)).to_metta()
        )
        metta.run(
            StateWrapperDefinition(AtFactPattern("apple", character.key)).to_metta()
        )
        metta.run(StateWrapperDefinition(AtFactPattern("coin", "cave")).to_metta())

        result_inventory = metta.run(f"!{inventory.to_metta()}")
        inventory_text = format_metta_output(result_inventory)
        self.assertIn("Worn sword", inventory_text)
        self.assertIn("Red apple", inventory_text)
        self.assertNotIn("hangs from your belt", inventory_text)
        self.assertNotIn("sits in your pouch", inventory_text)


if __name__ == "__main__":
    unittest.main()

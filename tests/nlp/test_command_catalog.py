import unittest

from core.definitions.facts.container_fact_definition import ContainerFactDefinition
from core.definitions.facts.item_fact_definition import ItemFactDefinition
from core.definitions.facts.location_fact_definition import LocationFactDefinition
from core.definitions.functions.inventory_function_definition import (
    InventoryFunctionPattern,
)
from core.definitions.functions.look_in_function_definition import (
    LookInFunctionDefinition,
)
from core.definitions.functions.move_to_function_definition import (
    MoveToFunctionDefinition,
)
from core.definitions.functions.move_towards_function_definition import (
    MoveTowardsFunctionDefinition,
)
from core.definitions.functions.pickup_function_definition import (
    PickUpFunctionDefinition,
)
from core.definitions.functions.examine_function_definition import (
    ExamineFunctionDefinition,
)
from core.definitions.functions.use_function_definition import UseFunctionDefinition
from core.nlp import build_command_catalog
from core.patterns.facts.character_fact_pattern import CharacterFactPattern
from core.world import World


class TestCommandCatalog(unittest.TestCase):
    def test_builds_commands_from_world_definitions(self):
        character = CharacterFactPattern("player", "John")

        world = World()
        world.add_definition(
            ItemFactDefinition("crescent_rock", "pick", "drop", "examine")
        )
        world.add_definition(ItemFactDefinition("compass", "pick", "drop", "examine"))
        world.add_definition(
            LocationFactDefinition("camping_site", "You are at the camp.")
        )
        world.add_definition(LocationFactDefinition("glade", "You are in the glade."))
        world.add_definition(ContainerFactDefinition("wooden_chest"))
        world.add_definition(InventoryFunctionPattern(character))
        world.add_definition(MoveToFunctionDefinition(character))
        world.add_definition(MoveTowardsFunctionDefinition(character))
        world.add_definition(PickUpFunctionDefinition(character))
        world.add_definition(LookInFunctionDefinition(character))
        world.add_definition(ExamineFunctionDefinition(character))
        world.add_definition(UseFunctionDefinition(character))

        catalog = build_command_catalog(world)
        utterance_to_metta = {entry.utterance: entry.metta for entry in catalog}

        self.assertEqual(
            utterance_to_metta.get("pickup crescent rock"), "(pickup (crescent_rock))"
        )
        self.assertEqual(
            utterance_to_metta.get("go to camping site"), "(move-to (camping_site))"
        )
        self.assertEqual(utterance_to_metta.get("go north"), "(move-towards (north))")
        self.assertEqual(utterance_to_metta.get("inventory"), "(inventory)")
        self.assertEqual(
            utterance_to_metta.get("use compass on crescent rock"),
            "(use (compass crescent_rock))",
        )
        self.assertEqual(
            utterance_to_metta.get("examine compass"),
            "(examine (compass))",
        )
        self.assertEqual(
            utterance_to_metta.get("check compass"),
            "(examine (compass))",
        )
        self.assertEqual(
            utterance_to_metta.get("look in wooden chest"),
            "(look-in (wooden_chest))",
        )


if __name__ == "__main__":
    unittest.main()

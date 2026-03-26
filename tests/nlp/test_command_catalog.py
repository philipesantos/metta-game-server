import unittest

from core.definitions.facts.container_fact_definition import ContainerFactDefinition
from core.definitions.facts.item_fact_definition import ItemFactDefinition
from core.definitions.facts.location_fact_definition import LocationFactDefinition
from core.definitions.functions.inventory_function_definition import (
    InventoryFunctionPattern,
)
from core.definitions.functions.drop_function_definition import (
    DropFunctionDefinition,
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
from core.definitions.functions.use_item_function_definition import (
    UseItemFunctionDefinition,
)
from core.nlp import build_command_catalog
from core.definitions.wrappers.state_wrapper_definition import StateWrapperDefinition
from core.patterns.facts.character_fact_pattern import CharacterFactPattern
from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.world import World
from modules.cave.functions.stay_still_function_definition import (
    StayStillFunctionDefinition,
)
from tests.utils.metta import get_test_metta


class TestCommandCatalog(unittest.TestCase):
    def test_builds_commands_from_runtime_metta_state(self):
        character = CharacterFactPattern("player", "John")
        metta = get_test_metta()

        world = World()
        world.add_definition(
            ItemFactDefinition("crescent_rock", "pick", "drop", "examine")
        )
        world.add_definition(ItemFactDefinition("compass", "pick", "drop", "examine"))
        world.add_definition(ItemFactDefinition("oil", "pick", "drop", "examine"))
        world.add_definition(
            LocationFactDefinition("camping_site", "You are at the camp.")
        )
        world.add_definition(LocationFactDefinition("glade", "You are in the glade."))
        world.add_definition(
            ContainerFactDefinition(
                "wooden_chest",
                text_contents="A wooden chest sits here.",
            )
        )
        world.add_definition(
            ContainerFactDefinition(
                "satchel",
                text_contents="A satchel rests here.",
                can_pickup=True,
            )
        )
        world.add_definition(
            ContainerFactDefinition(
                "well",
                name="Abandoned well",
                text_contents="An abandoned well opens in the ground here.",
            )
        )
        world.add_definition(InventoryFunctionPattern(character))
        world.add_definition(MoveToFunctionDefinition(character))
        world.add_definition(MoveTowardsFunctionDefinition(character))
        world.add_definition(PickUpFunctionDefinition(character))
        world.add_definition(DropFunctionDefinition(character))
        world.add_definition(LookInFunctionDefinition(character))
        world.add_definition(ExamineFunctionDefinition(character))
        world.add_definition(UseFunctionDefinition(character))
        world.add_definition(UseItemFunctionDefinition(character))
        world.add_definition(StayStillFunctionDefinition(character))
        world.add_definition(StateWrapperDefinition(AtFactPattern("player", "glade")))
        world.add_definition(
            StateWrapperDefinition(AtFactPattern("crescent_rock", "glade"))
        )
        world.add_definition(StateWrapperDefinition(AtFactPattern("compass", "player")))
        world.add_definition(StateWrapperDefinition(AtFactPattern("oil", "glade")))
        world.add_definition(
            StateWrapperDefinition(AtFactPattern("wooden_chest", "glade"))
        )
        world.add_definition(StateWrapperDefinition(AtFactPattern("satchel", "glade")))
        world.add_definition(StateWrapperDefinition(AtFactPattern("well", "glade")))

        metta.run(world.to_metta())
        catalog = build_command_catalog(world, metta)
        utterance_to_metta = {entry.utterance: entry.metta for entry in catalog}

        self.assertEqual(
            utterance_to_metta.get("pickup crescent rock"), "(pickup (crescent_rock))"
        )
        self.assertEqual(
            utterance_to_metta.get("get crescent rock"), "(pickup (crescent_rock))"
        )
        self.assertEqual(utterance_to_metta.get("get compass"), "(pickup (compass))")
        self.assertEqual(utterance_to_metta.get("get oil"), "(pickup (oil))")
        self.assertEqual(utterance_to_metta.get("get satchel"), "(pickup (satchel))")
        self.assertEqual(utterance_to_metta.get("pick satchel"), "(pickup (satchel))")
        self.assertEqual(utterance_to_metta.get("drop satchel"), "(drop (satchel))")
        self.assertEqual(
            utterance_to_metta.get("go to camping site"), "(move-to (camping_site))"
        )
        self.assertEqual(utterance_to_metta.get("go north"), "(move-towards (north))")
        self.assertEqual(utterance_to_metta.get("inventory"), "(inventory)")
        self.assertEqual(utterance_to_metta.get("check inventory"), "(inventory)")
        self.assertEqual(utterance_to_metta.get("what am i carrying"), "(inventory)")
        self.assertEqual(
            utterance_to_metta.get("what is in my inventory"), "(inventory)"
        )
        self.assertEqual(utterance_to_metta.get("check my bag"), "(inventory)")
        self.assertEqual(utterance_to_metta.get("what's in my bag"), "(inventory)")
        self.assertEqual(utterance_to_metta.get("stay still"), "(stay-still)")
        self.assertEqual(utterance_to_metta.get("wait"), "(stay-still)")
        self.assertEqual(
            utterance_to_metta.get("use compass on crescent rock"),
            "(use (compass crescent_rock))",
        )
        self.assertEqual(utterance_to_metta.get("use compass"), "(use (compass))")
        self.assertEqual(utterance_to_metta.get("activate compass"), "(use (compass))")
        self.assertEqual(utterance_to_metta.get("turn compass"), "(use (compass))")
        self.assertEqual(utterance_to_metta.get("turn on compass"), "(use (compass))")
        self.assertEqual(
            utterance_to_metta.get("examine compass"),
            "(examine (compass))",
        )
        self.assertEqual(
            utterance_to_metta.get("check compass"),
            "(examine (compass))",
        )
        self.assertEqual(
            utterance_to_metta.get("examine wooden chest"),
            "(examine (wooden_chest))",
        )
        self.assertEqual(
            utterance_to_metta.get("look in wooden chest"),
            "(look-in (wooden_chest))",
        )
        self.assertEqual(
            utterance_to_metta.get("open wooden chest"),
            "(look-in (wooden_chest))",
        )
        self.assertEqual(
            utterance_to_metta.get("search wooden chest"),
            "(look-in (wooden_chest))",
        )
        self.assertEqual(
            utterance_to_metta.get("look in well"),
            "(look-in (well))",
        )
        self.assertEqual(
            utterance_to_metta.get("look in abandoned well"),
            "(look-in (well))",
        )
        self.assertEqual(
            utterance_to_metta.get("open abandoned well"),
            "(look-in (well))",
        )

    def test_prefers_active_runtime_key_when_display_name_matches(self):
        character = CharacterFactPattern("player", "John")
        metta = get_test_metta()

        world = World()
        world.add_definition(
            ItemFactDefinition(
                "lantern",
                "pick",
                "drop",
                "dry lantern",
                name="Lantern",
            )
        )
        world.add_definition(
            ItemFactDefinition(
                "lantern_2",
                "pick",
                "drop",
                "fueled lantern",
                name="Lantern",
            )
        )
        world.add_definition(LocationFactDefinition("glade", "You are in the glade."))
        world.add_definition(InventoryFunctionPattern(character))
        world.add_definition(MoveToFunctionDefinition(character))
        world.add_definition(MoveTowardsFunctionDefinition(character))
        world.add_definition(PickUpFunctionDefinition(character))
        world.add_definition(DropFunctionDefinition(character))
        world.add_definition(LookInFunctionDefinition(character))
        world.add_definition(ExamineFunctionDefinition(character))
        world.add_definition(UseFunctionDefinition(character))
        world.add_definition(UseItemFunctionDefinition(character))
        world.add_definition(StayStillFunctionDefinition(character))
        world.add_definition(StateWrapperDefinition(AtFactPattern("player", "glade")))
        world.add_definition(
            StateWrapperDefinition(AtFactPattern("lantern_2", "glade"))
        )

        metta.run(world.to_metta())
        catalog = build_command_catalog(world, metta)
        utterance_to_metta = {entry.utterance: entry.metta for entry in catalog}

        self.assertEqual(
            utterance_to_metta.get("get lantern 2"), "(pickup (lantern_2))"
        )
        self.assertEqual(
            utterance_to_metta.get("examine lantern 2"), "(examine (lantern_2))"
        )

    def test_builds_aliases_from_explicit_entity_names(self):
        character = CharacterFactPattern("player", "John")
        metta = get_test_metta()

        world = World()
        world.add_definition(
            ContainerFactDefinition(
                "well",
                name="Abandoned well",
                text_contents="An abandoned well opens in the ground here.",
            )
        )
        world.add_definition(LookInFunctionDefinition(character))
        world.add_definition(ExamineFunctionDefinition(character))
        world.add_definition(StateWrapperDefinition(AtFactPattern("player", "well")))
        world.add_definition(StateWrapperDefinition(AtFactPattern("well", "well")))

        metta.run(world.to_metta())
        catalog = build_command_catalog(world, metta)
        utterance_to_metta = {entry.utterance: entry.metta for entry in catalog}

        self.assertEqual(utterance_to_metta.get("examine well"), "(examine (well))")
        self.assertEqual(
            utterance_to_metta.get("examine abandoned well"), "(examine (well))"
        )
        self.assertEqual(utterance_to_metta.get("open well"), "(look-in (well))")
        self.assertEqual(
            utterance_to_metta.get("open abandoned well"), "(look-in (well))"
        )


if __name__ == "__main__":
    unittest.main()

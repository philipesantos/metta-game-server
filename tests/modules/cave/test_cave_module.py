import unittest

from core.definitions.facts.container_fact_definition import ContainerFactDefinition
from core.definitions.facts.item_fact_definition import ItemFactDefinition
from core.definitions.functions.exists_function_definition import (
    ExistsFunctionDefinition,
)
from core.definitions.functions.use_item_function_definition import (
    UseItemFunctionDefinition,
)
from core.definitions.functions.trigger_function_definition import (
    TriggerFunctionDefinition,
)
from core.definitions.wrappers.state_wrapper_definition import StateWrapperDefinition
from core.definitions.facts.location_fact_definition import LocationFactDefinition
from core.patterns.events.examine_event_pattern import ExamineEventPattern
from core.patterns.events.move_event_pattern import MoveEventPattern
from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.patterns.facts.character_fact_pattern import CharacterFactPattern
from core.patterns.facts.item_fact_pattern import ItemFactPattern
from core.patterns.facts.location_fact_pattern import LocationFactPattern
from core.patterns.facts.route_block_fact_pattern import RouteBlockFactPattern
from core.patterns.facts.supported_use_fact_pattern import SupportedUseFactPattern
from core.patterns.functions.trigger_function_pattern import TriggerFunctionPattern
from core.patterns.functions.use_item_function_pattern import UseItemFunctionPattern
from core.patterns.wrappers.stale_wrapper_pattern import StaleWrapperPattern
from core.patterns.wrappers.state_wrapper_pattern import StateWrapperPattern
from core.world import World
from modules.cave.cave_module import CaveModule
from modules.cave.functions.stay_still_function_definition import (
    StayStillFunctionDefinition,
)
from modules.cave.patterns.bear_threat_pending_fact_pattern import (
    BearThreatPendingFactPattern,
)
from modules.cave.patterns.cave_lit_fact_pattern import CaveLitFactPattern
from modules.cave.patterns.stay_still_event_pattern import StayStillEventPattern
from modules.cave.patterns.stay_still_function_pattern import (
    StayStillFunctionPattern,
)
from tests.utils.metta import get_test_metta
from tests.utils.utils import unwrap_first_match
from utils.response import format_metta_output


class TestCaveModule(unittest.TestCase):
    def test_defines_cave_location_boulder_and_route_block(self):
        metta = get_test_metta()

        world = World()
        cave_entrance = LocationFactDefinition(
            "ridge", "A narrow ridge of pale stone rises above the glade."
        )
        character = CharacterFactPattern("player", "John")
        CaveModule(cave_entrance, character).apply(world)
        metta.run(world.to_metta())

        location_pattern = LocationFactPattern("cave")
        location_result = metta.run(
            f"!(match &self {location_pattern.to_metta()} {location_pattern.to_metta()})"
        )
        self.assertEqual(unwrap_first_match(location_result), location_pattern.to_metta())

        bear_pattern = CharacterFactPattern("bear", "Bear")
        bear_result = metta.run(
            f"!(match &self {bear_pattern.to_metta()} {bear_pattern.to_metta()})"
        )
        self.assertEqual(unwrap_first_match(bear_result), bear_pattern.to_metta())

        bear_enter_text_result = metta.run("!(match &self (EnterText bear $text) $text)")
        self.assertEqual(
            unwrap_first_match(bear_enter_text_result),
            "A massive bear looms in the darkness, ready to tear you apart.",
        )

        bear_state = StateWrapperPattern(AtFactPattern("bear", "cave"))
        bear_state_result = metta.run(
            f"!(match &self {bear_state.to_metta()} {bear_state.to_metta()})"
        )
        self.assertEqual(bear_state_result, [[]])

        boulder_state = StateWrapperPattern(
            AtFactPattern("huge_rock", "ridge")
        )
        boulder_result = metta.run(
            f"!(match &self {boulder_state.to_metta()} {boulder_state.to_metta()})"
        )
        self.assertEqual(unwrap_first_match(boulder_result), boulder_state.to_metta())

        route_block_pattern = RouteBlockFactPattern(
            "ridge", "cave", "$reason"
        )
        route_block_result = metta.run(
            f"!(match &self {route_block_pattern.to_metta()} $reason)"
        )
        self.assertEqual(
            unwrap_first_match(route_block_result),
            "A huge rock blocks the cave entrance.",
        )

    def test_registers_stay_still_function(self):
        world = World()
        cave_entrance = LocationFactDefinition(
            "ridge", "A narrow ridge of pale stone rises above the glade."
        )
        character = CharacterFactPattern("player", "John")

        CaveModule(cave_entrance, character).apply(world)

        self.assertTrue(
            any(
                isinstance(definition, StayStillFunctionDefinition)
                for definition in world.definitions
            )
        )

    def test_registers_stay_still_trigger_for_any_location(self):
        world = World()
        cave_entrance = LocationFactDefinition(
            "ridge", "A narrow ridge of pale stone rises above the glade."
        )
        character = CharacterFactPattern("player", "John")

        CaveModule(cave_entrance, character).apply(world)

        self.assertTrue(
            any(
                isinstance(definition, TriggerFunctionDefinition)
                and isinstance(definition.event, StayStillEventPattern)
                and definition.event.where == "$where"
                for definition in world.definitions
            )
        )

    def test_registers_lantern_and_oil_use_when_dependencies_are_provided(self):
        metta = get_test_metta()

        world = World()
        cave_entrance = LocationFactDefinition(
            "ridge", "A narrow ridge of pale stone rises above the glade."
        )
        character = CharacterFactPattern("player", "John")
        chest = ContainerFactDefinition(key="chest", name="Chest")

        world.add_definition(chest)
        CaveModule(
            cave_entrance,
            character,
            lantern_container=chest,
        ).apply(world)
        metta.run(world.to_metta())

        oil_pattern = ItemFactPattern("oil")
        oil_pattern_result = metta.run(
            f"!(match &self {oil_pattern.to_metta()} {oil_pattern.to_metta()})"
        )
        self.assertEqual(unwrap_first_match(oil_pattern_result), oil_pattern.to_metta())

        lantern_state = StateWrapperPattern(AtFactPattern("lantern", "chest"))
        lantern_state_result = metta.run(
            f"!(match &self {lantern_state.to_metta()} {lantern_state.to_metta()})"
        )
        self.assertEqual(unwrap_first_match(lantern_state_result), lantern_state.to_metta())

        supported_use = SupportedUseFactPattern("oil", "lantern")
        supported_use_result = metta.run(
            f"!(match &self {supported_use.to_metta()} {supported_use.to_metta()})"
        )
        self.assertEqual(
            unwrap_first_match(supported_use_result), supported_use.to_metta()
        )

    def test_using_functioning_lantern_in_cave_reveals_bear_and_arms_threat(self):
        metta = get_test_metta()

        world = World()
        cave_entrance = LocationFactDefinition(
            "ridge", "A narrow ridge of pale stone rises above the glade."
        )
        character = CharacterFactPattern("player", "John")
        chest = ContainerFactDefinition(key="chest", name="Chest")

        world.add_definition(ExistsFunctionDefinition())
        world.add_definition(UseItemFunctionDefinition(character))
        world.add_definition(chest)
        CaveModule(
            cave_entrance,
            character,
            lantern_container=chest,
        ).apply(world)
        world.add_definition(
            StateWrapperDefinition(AtFactPattern(character.key, "cave"))
        )
        world.add_definition(
            StateWrapperDefinition(AtFactPattern("functioning_lantern", character.key))
        )
        metta.run(world.to_metta())

        result = metta.run(f"!{UseItemFunctionPattern('functioning_lantern').to_metta()}")

        self.assertIn(
            "The lantern light spills across damp stone walls and old bones scattered across the cave floor. A massive bear looms in the darkness, ready to tear you apart.",
            format_metta_output(result),
        )

        bear_state = StateWrapperPattern(AtFactPattern("bear", "cave"))
        bear_state_result = metta.run(
            f"!(match &self {bear_state.to_metta()} {bear_state.to_metta()})"
        )
        self.assertEqual(unwrap_first_match(bear_state_result), bear_state.to_metta())

        lantern_state = StateWrapperPattern(
            AtFactPattern("functioning_lantern", character.key)
        )
        lantern_state_result = metta.run(
            f"!(match &self {lantern_state.to_metta()} {lantern_state.to_metta()})"
        )
        self.assertEqual(lantern_state_result, [[]])

        pending_state = StateWrapperPattern(BearThreatPendingFactPattern("player"))
        pending_result = metta.run(
            f"!(match &self {pending_state.to_metta()} {pending_state.to_metta()})"
        )
        self.assertEqual(unwrap_first_match(pending_result), pending_state.to_metta())

        cave_lit_state = StateWrapperPattern(CaveLitFactPattern("cave"))
        cave_lit_result = metta.run(
            f"!(match &self {cave_lit_state.to_metta()} {cave_lit_state.to_metta()})"
        )
        self.assertEqual(unwrap_first_match(cave_lit_result), cave_lit_state.to_metta())

    def test_using_functioning_lantern_places_configured_items_in_cave(self):
        metta = get_test_metta()

        world = World()
        cave_entrance = LocationFactDefinition(
            "ridge", "A narrow ridge of pale stone rises above the glade."
        )
        character = CharacterFactPattern("player", "John")
        chest = ContainerFactDefinition(key="chest", name="Chest")
        bone_charm = ItemFactDefinition(
            key="bone_charm",
            name="Bone charm",
            text_pickup="You pick up the bone charm.",
            text_drop="You drop the bone charm.",
            text_examine="The charm is carved from old bone and strung on a dark cord.",
            text_enter="A carved bone charm lies here.",
            text_look="A carved bone charm rests here.",
        )

        world.add_definition(ExistsFunctionDefinition())
        world.add_definition(UseItemFunctionDefinition(character))
        world.add_definition(chest)
        world.add_definition(bone_charm)
        CaveModule(
            cave_entrance,
            character,
            lantern_container=chest,
            cave_items_to_reveal=[bone_charm],
        ).apply(world)
        world.add_definition(
            StateWrapperDefinition(AtFactPattern(character.key, "cave"))
        )
        world.add_definition(
            StateWrapperDefinition(AtFactPattern("functioning_lantern", character.key))
        )
        metta.run(world.to_metta())

        hidden_item_state = StateWrapperPattern(AtFactPattern("bone_charm", "cave"))
        hidden_item_state_result = metta.run(
            f"!(match &self {hidden_item_state.to_metta()} {hidden_item_state.to_metta()})"
        )
        self.assertEqual(hidden_item_state_result, [[]])

        metta.run(f"!{UseItemFunctionPattern('functioning_lantern').to_metta()}")

        revealed_item_result = metta.run(
            f"!(match &self {hidden_item_state.to_metta()} {hidden_item_state.to_metta()})"
        )
        self.assertEqual(
            unwrap_first_match(revealed_item_result), hidden_item_state.to_metta()
        )

    def test_using_functioning_lantern_outside_cave_prints_no_use_message(self):
        metta = get_test_metta()

        world = World()
        cave_entrance = LocationFactDefinition(
            "ridge", "A narrow ridge of pale stone rises above the glade."
        )
        character = CharacterFactPattern("player", "John")
        chest = ContainerFactDefinition(key="chest", name="Chest")

        world.add_definition(ExistsFunctionDefinition())
        world.add_definition(UseItemFunctionDefinition(character))
        world.add_definition(chest)
        CaveModule(
            cave_entrance,
            character,
            lantern_container=chest,
        ).apply(world)
        world.add_definition(
            StateWrapperDefinition(AtFactPattern(character.key, "glade"))
        )
        world.add_definition(
            StateWrapperDefinition(AtFactPattern("functioning_lantern", character.key))
        )
        metta.run(world.to_metta())

        result = metta.run(f"!{UseItemFunctionPattern('functioning_lantern').to_metta()}")

        self.assertIn(
            "The lantern has no use here.",
            format_metta_output(result),
        )

    def test_entering_cave_before_lighting_shows_darkness_message(self):
        metta = get_test_metta()

        world = World()
        cave_entrance = LocationFactDefinition(
            "ridge", "A narrow ridge of pale stone rises above the glade."
        )
        character = CharacterFactPattern("player", "John")

        world.add_definition(ExistsFunctionDefinition())
        CaveModule(cave_entrance, character).apply(world)
        metta.run(world.to_metta())

        result = metta.run(f"!{TriggerFunctionPattern(MoveEventPattern('ridge', 'cave')).to_metta()}")

        self.assertIn(
            "The cave is pitch dark, and you cannot make out anything ahead.",
            format_metta_output(result),
        )

    def test_entering_cave_after_lighting_shows_cave_description(self):
        metta = get_test_metta()

        world = World()
        cave_entrance = LocationFactDefinition(
            "ridge", "A narrow ridge of pale stone rises above the glade."
        )
        character = CharacterFactPattern("player", "John")

        world.add_definition(ExistsFunctionDefinition())
        CaveModule(cave_entrance, character).apply(world)
        world.add_definition(StateWrapperDefinition(CaveLitFactPattern("cave")))
        metta.run(world.to_metta())

        result = metta.run(f"!{TriggerFunctionPattern(MoveEventPattern('ridge', 'cave')).to_metta()}")

        self.assertIn(
            "The lantern light spills across damp stone walls and old bones scattered across the cave floor.",
            format_metta_output(result),
        )

    def test_stay_still_prints_message_in_non_cave_location(self):
        metta = get_test_metta()

        world = World()
        cave_entrance = LocationFactDefinition(
            "ridge", "A narrow ridge of pale stone rises above the glade."
        )
        character = CharacterFactPattern("player", "John")

        world.add_definition(ExistsFunctionDefinition())
        CaveModule(cave_entrance, character).apply(world)
        metta.run(world.to_metta())
        metta.run(
            StateWrapperDefinition(AtFactPattern(character.key, "beach")).to_metta()
        )

        result = metta.run(f"!{StayStillFunctionPattern().to_metta()}")

        self.assertIn("You hold still for a moment.", str(result))

    def test_entering_cave_does_not_arm_bear_threat_before_lantern_use(self):
        metta = get_test_metta()

        world = World()
        cave_entrance = LocationFactDefinition(
            "ridge", "A narrow ridge of pale stone rises above the glade."
        )
        character = CharacterFactPattern("player", "John")

        CaveModule(cave_entrance, character).apply(world)
        metta.run(world.to_metta())

        trigger = TriggerFunctionPattern(MoveEventPattern("ridge", "cave"))
        metta.run(f"!{trigger.to_metta()}")

        pending_state = StateWrapperPattern(BearThreatPendingFactPattern("player"))
        pending_result = metta.run(
            f"!(match &self {pending_state.to_metta()} {pending_state.to_metta()})"
        )
        self.assertEqual(pending_result, [[]])

    def test_stay_still_clears_bear_threat_and_marks_tick_stale(self):
        metta = get_test_metta()

        world = World()
        cave_entrance = LocationFactDefinition(
            "ridge", "A narrow ridge of pale stone rises above the glade."
        )
        character = CharacterFactPattern("player", "John")

        world.add_definition(ExistsFunctionDefinition())
        CaveModule(cave_entrance, character).apply(world)
        metta.run(world.to_metta())
        metta.run(
            StateWrapperDefinition(BearThreatPendingFactPattern("player")).to_metta()
        )
        metta.run(
            StateWrapperDefinition(AtFactPattern(character.key, "cave")).to_metta()
        )
        metta.run(StateWrapperDefinition(AtFactPattern("bear", "cave")).to_metta())

        result = metta.run(f"!{StayStillFunctionPattern().to_metta()}")

        self.assertIn(
            "You remain perfectly still until the bear goes away. You are safe for now.",
            str(result),
        )

        pending_state = StateWrapperPattern(BearThreatPendingFactPattern("player"))
        pending_result = metta.run(
            f"!(match &self {pending_state.to_metta()} {pending_state.to_metta()})"
        )
        self.assertEqual(pending_result, [[]])

        bear_state = StateWrapperPattern(AtFactPattern("bear", "cave"))
        bear_result = metta.run(
            f"!(match &self {bear_state.to_metta()} {bear_state.to_metta()})"
        )
        self.assertEqual(bear_result, [[]])

        stale_tick = StaleWrapperPattern("Tick")
        stale_result = metta.run(f"!(match &self {stale_tick.to_metta()} True)")
        self.assertEqual(unwrap_first_match(stale_result), True)

    def test_stay_still_after_bear_threat_shows_revealed_cave_items(self):
        metta = get_test_metta()

        world = World()
        cave_entrance = LocationFactDefinition(
            "ridge", "A narrow ridge of pale stone rises above the glade."
        )
        character = CharacterFactPattern("player", "John")
        bone_charm = ItemFactDefinition(
            key="bone_charm",
            name="Bone charm",
            text_pickup="You pick up the bone charm.",
            text_drop="You drop the bone charm.",
            text_examine="The charm is carved from old bone and strung on a dark cord.",
            text_enter="A carved bone charm lies here.",
            text_look="A carved bone charm rests here.",
        )

        world.add_definition(ExistsFunctionDefinition())
        world.add_definition(bone_charm)
        CaveModule(
            cave_entrance,
            character,
            cave_items_to_reveal=[bone_charm],
        ).apply(world)
        metta.run(world.to_metta())
        metta.run(
            StateWrapperDefinition(BearThreatPendingFactPattern("player")).to_metta()
        )
        metta.run(
            StateWrapperDefinition(AtFactPattern(character.key, "cave")).to_metta()
        )
        metta.run(StateWrapperDefinition(AtFactPattern("bear", "cave")).to_metta())
        metta.run(
            StateWrapperDefinition(AtFactPattern("bone_charm", "cave")).to_metta()
        )

        result = metta.run(f"!{StayStillFunctionPattern().to_metta()}")
        output = format_metta_output(result)

        self.assertIn(
            "You remain perfectly still until the bear goes away. You are safe for now.",
            output,
        )
        self.assertIn("A carved bone charm lies here.", output)

    def test_moving_without_staying_still_prints_death_message(self):
        metta = get_test_metta()

        world = World()
        cave_entrance = LocationFactDefinition(
            "ridge", "A narrow ridge of pale stone rises above the glade."
        )
        character = CharacterFactPattern("player", "John")

        CaveModule(cave_entrance, character).apply(world)
        metta.run(world.to_metta())
        metta.run(
            StateWrapperDefinition(BearThreatPendingFactPattern("player")).to_metta()
        )

        trigger = TriggerFunctionPattern(MoveEventPattern("cave", "glade"))
        result = metta.run(f"!{trigger.to_metta()}")

        self.assertIn(
            "The bear lunges before you can react and tears you apart. You died.",
            format_metta_output(result),
        )

        pending_state = StateWrapperPattern(BearThreatPendingFactPattern("player"))
        pending_result = metta.run(
            f"!(match &self {pending_state.to_metta()} {pending_state.to_metta()})"
        )
        self.assertEqual(pending_result, [[]])

    def test_examine_does_not_consume_bear_threat(self):
        metta = get_test_metta()

        world = World()
        cave_entrance = LocationFactDefinition(
            "ridge", "A narrow ridge of pale stone rises above the glade."
        )
        character = CharacterFactPattern("player", "John")

        CaveModule(cave_entrance, character).apply(world)
        metta.run(world.to_metta())
        metta.run(
            StateWrapperDefinition(BearThreatPendingFactPattern("player")).to_metta()
        )

        trigger = TriggerFunctionPattern(ExamineEventPattern("bear"))
        metta.run(f"!{trigger.to_metta()}")

        pending_state = StateWrapperPattern(BearThreatPendingFactPattern("player"))
        pending_result = metta.run(
            f"!(match &self {pending_state.to_metta()} {pending_state.to_metta()})"
        )
        self.assertEqual(unwrap_first_match(pending_result), pending_state.to_metta())


if __name__ == "__main__":
    unittest.main()

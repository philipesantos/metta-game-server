import unittest
from unittest.mock import patch

from core.definitions.facts.container_fact_definition import ContainerFactDefinition
from core.definitions.facts.location_fact_definition import LocationFactDefinition
from core.definitions.facts.route_block_fact_definition import RouteBlockFactDefinition
from core.definitions.functions.exists_function_definition import (
    ExistsFunctionDefinition,
)
from core.definitions.functions.first_function_definition import (
    FirstFunctionDefinition,
)
from core.definitions.functions.last_function_definition import (
    LastFunctionDefinition,
)
from core.definitions.functions.location_path_function_definition import (
    LocationPathFunctionDefinition,
)
from core.definitions.functions.pickup_function_definition import (
    PickUpFunctionDefinition,
)
from core.definitions.functions.trigger_function_definition import (
    TriggerFunctionDefinition,
)
from core.definitions.functions.use_function_definition import UseFunctionDefinition
from core.definitions.side_effects.on_pickup_update_at import OnPickUpUpdateAt
from core.definitions.wrappers.state_wrapper_definition import StateWrapperDefinition
from core.patterns.events.pickup_event_pattern import PickUpEventPattern
from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.patterns.facts.character_fact_pattern import CharacterFactPattern
from core.patterns.facts.route_block_fact_pattern import RouteBlockFactPattern
from core.patterns.facts.tick_fact_pattern import TickFactPattern
from core.patterns.functions.pickup_function_pattern import PickUpFunctionPattern
from core.patterns.functions.use_function_pattern import UseFunctionPattern
from core.patterns.wrappers.state_wrapper_pattern import StateWrapperPattern
from core.world import World
from modules.cave.cave_entrance_block import CaveEntranceBlock
from modules.statues.statues_module import StatuesModule
from tests.utils.metta import get_test_metta
from tests.utils.utils import unwrap_first_match
from utils.response import format_metta_output


class TestStatuesModule(unittest.TestCase):
    def _build_statues_world(self):
        metta = get_test_metta()

        world = World()
        ridge = LocationFactDefinition("ridge", "A narrow ridge.")
        character = CharacterFactPattern("player", "John")
        containers = [
            ContainerFactDefinition("box_one"),
            ContainerFactDefinition("box_two"),
            ContainerFactDefinition("box_three"),
        ]

        world.add_definition(ExistsFunctionDefinition())
        world.add_definition(LocationPathFunctionDefinition())
        world.add_definition(FirstFunctionDefinition())
        world.add_definition(LastFunctionDefinition())
        world.add_definition(PickUpFunctionDefinition(character))
        world.add_definition(UseFunctionDefinition(character))
        world.add_definition(
            TriggerFunctionDefinition(
                PickUpEventPattern("$what", "$where"),
                [OnPickUpUpdateAt(character)],
            )
        )
        world.add_definition(ridge)
        world.add_definition(StateWrapperDefinition(AtFactPattern("player", "ridge")))
        world.add_definition(StateWrapperDefinition(TickFactPattern("1")))
        world.add_definition(StateWrapperDefinition(AtFactPattern("huge_rock", "ridge")))
        for container in containers:
            world.add_definition(container)
            world.add_definition(
                StateWrapperDefinition(AtFactPattern(container.key, "ridge"))
            )
        world.add_definition(
            RouteBlockFactDefinition(
                "ridge",
                "cave",
                "A huge rock blocks the cave entrance.",
            )
        )
        cave_entrance_block = CaveEntranceBlock(
            "huge_rock",
            "ridge",
            "ridge",
            "cave",
            "A huge rock blocks the cave entrance.",
        )

        with patch(
            "modules.statues.statues_module.random.sample",
            side_effect=lambda items, count: items[:count],
        ):
            StatuesModule(
                character,
                ridge,
                containers,
                cave_entrance_block=cave_entrance_block,
            ).apply(world)

        metta.run(world.to_metta())
        return metta

    def test_using_rune_on_empty_statue_places_it(self):
        metta = self._build_statues_world()

        metta.run(f"!{PickUpFunctionPattern('epsilon_rune').to_metta()}")
        result = metta.run(f"!{UseFunctionPattern('epsilon_rune', 'lion_statue').to_metta()}")

        self.assertIn(
            "You place the epsilon rune into the lion statue.",
            format_metta_output(result),
        )

        rune_state = StateWrapperPattern(AtFactPattern("epsilon_rune", "lion_statue"))
        rune_result = metta.run(
            f"!(match &self {rune_state.to_metta()} {rune_state.to_metta()})"
        )
        self.assertEqual(unwrap_first_match(rune_result), rune_state.to_metta())

    def test_correct_ego_order_triggers_success_message(self):
        metta = self._build_statues_world()

        for rune_key in ("epsilon_rune", "gamma_rune", "omicron_rune"):
            metta.run(f"!{PickUpFunctionPattern(rune_key).to_metta()}")

        metta.run(f"!{UseFunctionPattern('epsilon_rune', 'lion_statue').to_metta()}")
        metta.run(f"!{UseFunctionPattern('gamma_rune', 'eagle_statue').to_metta()}")
        result = metta.run(
            f"!{UseFunctionPattern('omicron_rune', 'bear_statue').to_metta()}"
        )

        self.assertIn(
            "The runes flare to life, spelling EGO across the statues. In the distance, the great boulder at the cave entrance grinds aside.",
            format_metta_output(result),
        )

        boulder_state = StateWrapperPattern(AtFactPattern("huge_rock", "ridge"))
        boulder_result = metta.run(
            f"!(match &self {boulder_state.to_metta()} {boulder_state.to_metta()})"
        )
        self.assertEqual(boulder_result, [[]])

        route_block = RouteBlockFactPattern(
            "ridge",
            "cave",
            "A huge rock blocks the cave entrance.",
        )
        route_block_result = metta.run(
            f"!(match &self {route_block.to_metta()} {route_block.to_metta()})"
        )
        self.assertEqual(route_block_result, [[]])

    def test_wrong_order_allows_rune_to_be_picked_back_up_from_statue(self):
        metta = self._build_statues_world()

        for rune_key in ("epsilon_rune", "gamma_rune", "omicron_rune"):
            metta.run(f"!{PickUpFunctionPattern(rune_key).to_metta()}")

        metta.run(f"!{UseFunctionPattern('gamma_rune', 'lion_statue').to_metta()}")
        metta.run(f"!{UseFunctionPattern('epsilon_rune', 'eagle_statue').to_metta()}")
        result = metta.run(
            f"!{UseFunctionPattern('omicron_rune', 'bear_statue').to_metta()}"
        )

        self.assertIn("Nothing happens.", format_metta_output(result))

        metta.run(f"!{PickUpFunctionPattern('gamma_rune').to_metta()}")
        inventory_state = StateWrapperPattern(AtFactPattern("gamma_rune", "player"))
        inventory_result = metta.run(
            f"!(match &self {inventory_state.to_metta()} {inventory_state.to_metta()})"
        )
        self.assertEqual(
            unwrap_first_match(inventory_result), inventory_state.to_metta()
        )

    def test_using_rune_on_filled_statue_shows_existing_rune_name(self):
        metta = self._build_statues_world()

        for rune_key in ("epsilon_rune", "gamma_rune"):
            metta.run(f"!{PickUpFunctionPattern(rune_key).to_metta()}")

        metta.run(f"!{UseFunctionPattern('epsilon_rune', 'lion_statue').to_metta()}")
        result = metta.run(f"!{UseFunctionPattern('gamma_rune', 'lion_statue').to_metta()}")

        self.assertIn(
            "The lion statue already holds the epsilon rune.",
            format_metta_output(result),
        )


if __name__ == "__main__":
    unittest.main()

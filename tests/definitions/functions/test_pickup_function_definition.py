import unittest

from core.definitions.facts.location_fact_definition import LocationFactDefinition
from core.definitions.functions.first_function_definition import (
    FirstFunctionDefinition,
)
from core.definitions.functions.exists_function_definition import (
    ExistsFunctionDefinition,
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
from core.definitions.side_effects.on_event_print import OnEventPrint
from core.definitions.wrappers.state_wrapper_definition import StateWrapperDefinition
from core.patterns.events.pickup_event_pattern import PickUpEventPattern
from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.patterns.facts.character_fact_pattern import CharacterFactPattern
from core.patterns.functions.pickup_function_pattern import PickUpFunctionPattern
from tests.utils.metta import get_test_metta

from tests.utils.utils import unwrap_first_match


class TestPickUpFunctionDefinition(unittest.TestCase):
    @staticmethod
    def _register_pickup_functions(metta):
        metta.run(LocationPathFunctionDefinition().to_metta())
        metta.run(FirstFunctionDefinition().to_metta())
        metta.run(LastFunctionDefinition().to_metta())
        metta.run(ExistsFunctionDefinition().to_metta())
        metta.run(
            TriggerFunctionDefinition(
                PickUpEventPattern("$what", "$where"),
                [OnEventPrint("Picked up")],
            ).to_metta()
        )

    def test_pickup(self):
        metta = get_test_metta()

        character = CharacterFactPattern("player", "John")

        self._register_pickup_functions(metta)
        metta.run(PickUpFunctionDefinition(character).to_metta())

        metta.run(LocationFactDefinition("glade", "A quiet glade.").to_metta())
        metta.run(
            StateWrapperDefinition(AtFactPattern(character.key, "glade")).to_metta()
        )
        metta.run(StateWrapperDefinition(AtFactPattern("coin", "chest")).to_metta())
        metta.run(StateWrapperDefinition(AtFactPattern("chest", "glade")).to_metta())

        pickup = PickUpFunctionPattern("coin")
        result_pickup = metta.run(f"!{pickup.to_metta()}")
        self.assertEqual(unwrap_first_match(result_pickup).text, "Picked up")

    def test_pickup_missing_item(self):
        metta = get_test_metta()

        character = CharacterFactPattern("player", "John")

        self._register_pickup_functions(metta)
        metta.run(PickUpFunctionDefinition(character).to_metta())

        metta.run(LocationFactDefinition("glade", "A quiet glade.").to_metta())
        metta.run(LocationFactDefinition("cave", "A dark cave.").to_metta())
        metta.run(
            StateWrapperDefinition(AtFactPattern(character.key, "cave")).to_metta()
        )
        metta.run(StateWrapperDefinition(AtFactPattern("coin", "chest")).to_metta())
        metta.run(StateWrapperDefinition(AtFactPattern("chest", "glade")).to_metta())

        pickup = PickUpFunctionPattern("coin")
        result_pickup = metta.run(f"!{pickup.to_metta()}")
        self.assertEqual(
            unwrap_first_match(result_pickup).text,
            "There is no such item",
        )


if __name__ == "__main__":
    unittest.main()

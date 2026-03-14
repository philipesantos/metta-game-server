from core.definitions.facts.character_fact_definition import CharacterFactDefinition
from core.definitions.facts.item_fact_definition import ItemFactDefinition
from core.definitions.facts.location_fact_definition import LocationFactDefinition
from core.definitions.facts.route_block_fact_definition import RouteBlockFactDefinition
from core.definitions.functions.trigger_function_definition import (
    TriggerFunctionDefinition,
)
from core.definitions.side_effects.on_event_print import OnEventPrint
from core.definitions.wrappers.state_wrapper_definition import StateWrapperDefinition
from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.patterns.facts.character_fact_pattern import CharacterFactPattern
from core.world import World
from modules.module import Module
from modules.cave.functions.stay_still_function_definition import (
    StayStillFunctionDefinition,
)
from modules.cave.patterns.stay_still_event_pattern import StayStillEventPattern


class CaveModule(Module):
    def __init__(
        self,
        cave_entrance_location: LocationFactDefinition,
        character: CharacterFactPattern,
    ):
        self.cave_entrance_location = cave_entrance_location
        self.character = character
        self.cave_location = LocationFactDefinition(
            key="cave", text_move_to="You are in the cave."
        )
        self.bear = CharacterFactDefinition(
            key="bear",
            name="Bear",
            text_enter="A massive bear looms in the darkness, ready to tear you apart.",
        )
        self.boulder = ItemFactDefinition(
            key="huge_rock",
            name="Huge rock",
            text_pickup="",
            text_drop="",
            text_examine="A massive boulder blocks the cave entrance. You cannot move it by hand.",
            text_enter="A cave entrance is here, but a huge rock blocks it.",
            text_look="The rock is wedged tightly in place, completely sealing the path ahead.",
            can_pickup=False,
        )

    def apply(self, world: World) -> None:
        world.add_definition(StayStillFunctionDefinition(self.character))
        world.add_definition(
            TriggerFunctionDefinition(
                StayStillEventPattern("$where"),
                [OnEventPrint("You stand still.")],
            )
        )
        world.add_definition(self.cave_location)
        world.add_definition(self.bear)
        world.add_definition(self.boulder)
        world.add_definition(
            StateWrapperDefinition(AtFactPattern(self.bear.key, self.cave_location.key))
        )
        world.add_definition(
            StateWrapperDefinition(
                AtFactPattern(self.boulder.key, self.cave_entrance_location.key)
            )
        )
        world.add_definition(
            RouteBlockFactDefinition(
                self.cave_entrance_location.key,
                self.cave_location.key,
                "A huge rock blocks the cave entrance.",
            )
        )

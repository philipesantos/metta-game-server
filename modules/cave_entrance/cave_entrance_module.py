from core.definitions.facts.item_fact_definition import ItemFactDefinition
from core.definitions.functions.trigger_function_definition import (
    TriggerFunctionDefinition,
)
from core.definitions.side_effects.on_event_print import OnEventPrint
from core.definitions.wrappers.state_wrapper_definition import StateWrapperDefinition
from core.patterns.events.use_event_pattern import UseEventPattern
from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.world import World
from modules.module import Module


class CaveEntranceModule(Module):
    def __init__(self, rock_location: str, cave_location: str):
        self.rock_location = rock_location
        self.cave_location = cave_location

    def apply(self, world: World) -> None:
        crescent_rock = ItemFactDefinition(
            key="crescent_rock",
            name="Crescent-moon rock",
            text_pickup="You pick up a crescent-moon rock.",
            text_drop="You drop the crescent-moon rock.",
            text_examine="The stone is cool and shaped like a crescent moon.",
            text_enter="A crescent-moon rock rests near your feet.",
            text_look="Inside, a crescent-moon rock catches the light.",
        )
        cave_door = ItemFactDefinition(
            key="cave_door",
            name="Carved stone door",
            text_pickup="",
            text_drop="",
            text_examine="A carved door with a crescent-shaped recess.",
            text_enter="A carved stone door stands sealed in the wall.",
            text_look="Inside, a carved stone door blocks the passage.",
            can_pickup=False,
        )
        world.add_definition(crescent_rock)
        world.add_definition(cave_door)
        world.add_definition(
            StateWrapperDefinition(AtFactPattern(crescent_rock.key, self.rock_location))
        )
        world.add_definition(
            StateWrapperDefinition(AtFactPattern(cave_door.key, self.cave_location))
        )
        world.add_definition(
            TriggerFunctionDefinition(
                UseEventPattern(crescent_rock.key, cave_door.key),
                [OnEventPrint("The cave door opens.")],
            )
        )

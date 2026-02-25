from core.definitions.facts.item_fact_definition import ItemFactDefinition
from core.definitions.facts.route_block_fact_definition import RouteBlockFactDefinition
from core.definitions.facts.route_fact_definition import RouteFactDefinition
from core.definitions.functions.trigger_function_definition import (
    TriggerFunctionDefinition,
)
from core.definitions.wrappers.state_wrapper_definition import StateWrapperDefinition
from core.patterns.events.pickup_event_pattern import PickUpEventPattern
from core.patterns.events.move_event_pattern import MoveEventPattern
from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.patterns.facts.character_fact_pattern import CharacterFactPattern
from core.world import World
from modules.compass.functions.compass_directions_function_definition import (
    CompassDirectionsFunctionDefinition,
)
from modules.compass.side_effects.compass_module_on_move_print_directions import (
    CompassModuleOnMovePrintDirections,
)
from modules.compass.side_effects.compass_module_on_pickup_print_directions import (
    CompassModuleOnPickupPrintDirections,
)
from modules.compass.side_effects.compass_module_on_pickup_remove_route_blocks import (
    CompassModuleOnPickupRemoveRouteBlocks,
)
from modules.module import Module


class CompassModule(Module):
    def __init__(
        self,
        character: CharacterFactPattern,
        initial_location: str,
        compass_where: str | None = None,
    ):
        self.character: CharacterFactPattern = character
        self.initial_location: str = initial_location
        self.compass_where: str = compass_where or initial_location

    def apply(self, world: World) -> None:
        item_compass = ItemFactDefinition(
            key="compass",
            name="Compass",
            text_pickup="You got the compass",
            text_drop="You dropped the compass",
            text_examine="An old compass etched with cardinal marks.",
            text_enter="An old compass lies here, its needle trembling.",
            text_look="Inside, an old compass rests against the lining.",
        )
        world.add_definition(item_compass)
        world.add_definition(CompassDirectionsFunctionDefinition())
        world.add_definition(
            StateWrapperDefinition(AtFactPattern(item_compass.key, self.compass_where))
        )
        world.add_definition(
            TriggerFunctionDefinition(
                MoveEventPattern("$from", "$to"),
                [CompassModuleOnMovePrintDirections(self.character)],
            )
        )
        world.add_definition(
            TriggerFunctionDefinition(
                PickUpEventPattern(item_compass.key, "$where"),
                [
                    CompassModuleOnPickupPrintDirections(self.character),
                    CompassModuleOnPickupRemoveRouteBlocks(),
                ],
            )
        )
        self._add_route_blocks_for_compass_location(world)

    def _add_route_blocks_for_compass_location(self, world: World) -> None:
        route_block_reason = "You hesitate. This isn’t a place to wander blindly."
        destinations: set[str] = set()
        for definition in world.definitions:
            if (
                isinstance(definition, RouteFactDefinition)
                and definition.location_from == self.initial_location
            ):
                destinations.add(definition.location_to)

        for destination in destinations:
            world.add_definition(
                RouteBlockFactDefinition(
                    self.initial_location,
                    destination,
                    route_block_reason,
                )
            )

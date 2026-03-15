from core.definitions.facts.container_fact_definition import ContainerFactDefinition
from core.definitions.facts.item_fact_definition import ItemFactDefinition
from core.definitions.facts.location_fact_definition import LocationFactDefinition
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
        initial_location: LocationFactDefinition,
        satchel_where: str | None = None,
    ):
        self.character: CharacterFactPattern = character
        self.initial_location: LocationFactDefinition = initial_location
        self.satchel_where: str = satchel_where or initial_location.key

    def apply(self, world: World) -> None:
        satchel = ContainerFactDefinition(
            key="satchel",
            name="Traveler's satchel",
            text_enter="A traveler's satchel rests here in the grass.",
            text_examine="A weathered traveler's satchel with a frayed strap and a half-open flap.",
            text_look="You open the satchel and look inside.",
            text_contents="A traveler's satchel rests in the grass.",
            text_pickup="You pick up the satchel.",
            text_drop="You set the satchel down.",
            can_pickup=True,
        )
        item_compass = ItemFactDefinition(
            key="compass",
            name="Compass",
            text_pickup="You pick up the compass.",
            text_drop="You set the compass down.",
            text_examine=(
                "A weathered compass rests in your palm, its needle still twitching "
                "toward north."
            ),
            text_look="Inside, an old compass rests against the lining.",
        )
        world.add_definition(satchel)
        world.add_definition(item_compass)
        world.add_definition(CompassDirectionsFunctionDefinition())
        world.add_definition(
            StateWrapperDefinition(AtFactPattern(satchel.key, self.satchel_where))
        )
        world.add_definition(
            StateWrapperDefinition(AtFactPattern(item_compass.key, satchel.key))
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
                    CompassModuleOnPickupRemoveRouteBlocks(self.initial_location.key),
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
                and definition.location_from == self.initial_location.key
            ):
                destinations.add(definition.location_to)

        for destination in destinations:
            world.add_definition(
                RouteBlockFactDefinition(
                    self.initial_location.key,
                    destination,
                    route_block_reason,
                )
            )

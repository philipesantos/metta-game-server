from core.definitions.facts.container_fact_definition import ContainerFactDefinition
from core.definitions.facts.item_fact_definition import ItemFactDefinition
from core.definitions.facts.location_fact_definition import LocationFactDefinition
from core.definitions.facts.route_block_fact_definition import RouteBlockFactDefinition
from core.definitions.functions.trigger_function_definition import (
    TriggerFunctionDefinition,
)
from core.definitions.side_effects.on_event_print import OnEventPrint
from core.definitions.wrappers.state_wrapper_definition import StateWrapperDefinition
from core.patterns.events.use_event_pattern import UseEventPattern
from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.world import World
from modules.cabin.side_effects.cabin_module_on_use_unlock import (
    CabinModuleOnUseUnlock,
)
from modules.module import Module


class CabinModule(Module):
    def __init__(
        self,
        path_location: LocationFactDefinition,
        cabin_location: LocationFactDefinition,
        key_container: ContainerFactDefinition,
        fireplace_items: list[ItemFactDefinition] | None = None,
    ):
        self.path_location = path_location
        self.cabin_location = cabin_location
        self.key_container = key_container
        self.fireplace_items = fireplace_items or []

    def apply(self, world: World) -> None:
        fireplace = ContainerFactDefinition(
            key="fireplace",
            name="Stone fireplace",
            text_enter="You see a stone fireplace built into the wall.",
            text_examine="A thin layer of ash rests at the bottom. The soot above suggests it hasn't been lit for quite some time.",
            text_look="You peer inside the fireplace.",
        )
        world.add_definition(fireplace)
        world.add_definition(
            StateWrapperDefinition(AtFactPattern(fireplace.key, self.cabin_location.key))
        )
        for item in self.fireplace_items:
            world.add_definition(
                StateWrapperDefinition(AtFactPattern(item.key, fireplace.key))
            )

        loose_board = ContainerFactDefinition(
            key="loose_board",
            name="Loose board",
            text_enter="One of the wooden boards looks slightly out of place.",
            text_examine="The board shifts when you press it. There seems to be space beneath it.",
            text_look="You crouch down and inspect the gap beneath the board.",
        )
        world.add_definition(loose_board)
        world.add_definition(
            StateWrapperDefinition(AtFactPattern(loose_board.key, self.cabin_location.key))
        )

        metal_key = ItemFactDefinition(
            key="metal_key",
            name="Metal key",
            text_enter="You see a small metal key.",
            text_examine="A small iron key with the word 'Cabin' faintly etched into its surface.",
            text_look="Inside, a small metal key.",
            text_drop="You drop the metal key.",
            text_pickup="You pick up the metal key.",
        )
        world.add_definition(metal_key)
        world.add_definition(
            StateWrapperDefinition(AtFactPattern(metal_key.key, self.key_container.key))
        )

        world.add_definition(
            RouteBlockFactDefinition(
                self.path_location.key,
                self.cabin_location.key,
                "The cabin is locked. You need a key.",
            )
        )
        world.add_definition(
            StateWrapperDefinition(
                AtFactPattern(self.cabin_location.key, self.path_location.key)
            )
        )
        world.add_definition(
            TriggerFunctionDefinition(
                UseEventPattern("metal_key", "cabin"),
                [
                    CabinModuleOnUseUnlock(
                        self.path_location.key, self.cabin_location.key
                    ),
                    OnEventPrint("You unlock the cabin door."),
                ],
            )
        )

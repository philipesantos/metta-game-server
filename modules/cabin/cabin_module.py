from core.definitions.facts.container_fact_definition import ContainerFactDefinition
from core.definitions.facts.item_fact_definition import ItemFactDefinition
from core.definitions.facts.location_fact_definition import LocationFactDefinition
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
        cabin_location: LocationFactDefinition,
        key_container: ContainerFactDefinition,
        fireplace_items: list[ItemFactDefinition] | None = None,
    ):
        self.cabin_location = cabin_location
        self.key_container = key_container
        self.fireplace_items = fireplace_items or []

    def apply(self, world: World) -> None:
        locked_cabin = ContainerFactDefinition(
            key="cabin",
            name="Locked cabin",
            text_enter="A weathered locked cabin stands just off the path.",
            text_examine="The cabin door is shut tight. A metal lock hangs from the latch.",
            text_look="The cabin is locked.",
            text_contents="A weathered locked cabin stands just off the path.",
        )
        world.add_definition(locked_cabin)
        world.add_definition(
            StateWrapperDefinition(AtFactPattern(locked_cabin.key, self.cabin_location.key))
        )

        cabin_container = ContainerFactDefinition(
            key="cabin",
            name="Cabin",
            text_enter="A weathered cabin stands just off the path.",
            text_examine="The cabin looks abandoned, but you can peer inside from the doorway.",
            text_look="You look inside the cabin.",
            text_contents="A weathered cabin stands just off the path.",
        )

        fireplace = ContainerFactDefinition(
            key="fireplace",
            name="Stone fireplace",
            text_enter="You see a stone fireplace built into the wall.",
            text_examine="A thin layer of ash rests at the bottom. The soot above suggests it hasn't been lit for quite some time.",
            text_look="You peer inside the fireplace.",
            text_contents="A cold stone fireplace is built into the far wall.",
        )
        world.add_definition(fireplace)
        world.add_definition(
            StateWrapperDefinition(AtFactPattern(fireplace.key, cabin_container.key))
        )

        loose_board = ContainerFactDefinition(
            key="loose_board",
            name="Loose board",
            text_enter="One of the wooden boards looks slightly out of place.",
            text_examine="The board shifts when you press it. There seems to be space beneath it.",
            text_look="You crouch down and inspect the gap beneath the board.",
            text_contents="One floorboard near the wall sits slightly loose.",
        )
        world.add_definition(loose_board)
        world.add_definition(
            StateWrapperDefinition(AtFactPattern(loose_board.key, cabin_container.key))
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
        for item in self.fireplace_items:
            world.add_definition(
                StateWrapperDefinition(AtFactPattern(item.key, fireplace.key))
            )
        world.add_definition(
            TriggerFunctionDefinition(
                UseEventPattern("metal_key", "cabin"),
                [
                    CabinModuleOnUseUnlock(
                        self.cabin_location.key, locked_cabin, cabin_container, metal_key
                    ),
                    OnEventPrint("You unlock the cabin door."),
                ],
            )
        )

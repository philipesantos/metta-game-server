from core.definitions.facts.container_fact_definition import ContainerFactDefinition
from core.definitions.facts.item_fact_definition import ItemFactDefinition
from core.definitions.facts.location_fact_definition import LocationFactDefinition
from core.definitions.functions.trigger_function_definition import (
    TriggerFunctionDefinition,
)
from core.definitions.side_effects.on_event_print import OnEventPrint
from core.definitions.side_effects.on_use_combine_item import OnUseCombineItem
from core.definitions.wrappers.state_wrapper_definition import StateWrapperDefinition
from core.patterns.events.use_event_pattern import UseEventPattern
from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.world import World
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
            key="locked_cabin",
            name="Locked cabin",
            text_enter="A weathered cabin stands here, its door locked shut.",
            text_examine=(
                "The warped door is held closed by a rusted metal lock hanging from "
                "the latch."
            ),
            text_look="The cabin is locked.",
            text_contents="A weathered locked cabin stands just off the path.",
        )
        world.add_definition(locked_cabin)
        world.add_definition(
            StateWrapperDefinition(
                AtFactPattern(locked_cabin.key, self.cabin_location.key)
            )
        )

        cabin_container = ContainerFactDefinition(
            key="cabin",
            name="Cabin",
            text_enter="A weathered cabin stands just off the path here.",
            text_examine=(
                "The cabin looks long abandoned, though the open doorway still lets "
                "you peer inside."
            ),
            text_look="You look inside the cabin.",
            text_contents="A weathered cabin stands just off the path.",
        )
        world.add_definition(cabin_container)

        fireplace = ContainerFactDefinition(
            key="fireplace",
            name="Stone fireplace",
            text_enter="A cold stone fireplace is built into the wall here.",
            text_examine=(
                "A thin bed of ash rests at the bottom, and the soot above suggests "
                "it has not been lit in a long while."
            ),
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
            text_enter="One loose floorboard sits here, raised slightly from the others.",
            text_examine=(
                "The board shifts under your touch, leaving a narrow gap that hints "
                "at empty space beneath the floor."
            ),
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
            text_enter="A small metal key rests here.",
            text_examine=(
                "The iron key is small and cold, with the word 'Cabin' faintly "
                "etched into its surface."
            ),
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
                UseEventPattern("metal_key", "locked_cabin"),
                [
                    OnUseCombineItem(locked_cabin, metal_key, cabin_container),
                    OnEventPrint("You unlock the cabin door."),
                ],
            )
        )

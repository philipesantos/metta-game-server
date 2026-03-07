import random

from core.definitions.facts.container_fact_definition import ContainerFactDefinition
from core.definitions.facts.item_fact_definition import ItemFactDefinition
from core.definitions.facts.location_fact_definition import LocationFactDefinition
from core.definitions.functions.trigger_function_definition import TriggerFunctionDefinition
from core.definitions.side_effects.on_event_print import OnEventPrint
from core.definitions.wrappers.state_wrapper_definition import StateWrapperDefinition
from core.patterns.events.move_event_pattern import MoveEventPattern
from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.patterns.facts.character_fact_pattern import CharacterFactPattern
from core.world import World
from modules.module import Module


class StatuesModule(Module):
    def __init__(
        self,
        character: CharacterFactPattern,
        statue_location: LocationFactDefinition,
        tablets_possible_containers: list[ContainerFactDefinition],
    ):
        if len(tablets_possible_containers) < 3:
            raise ValueError(
                "tablets_possible_containers must contain at least 3 containers."
            )
        self.character: CharacterFactPattern = character
        self.statue_location: LocationFactDefinition = statue_location
        self.tablets_possible_containers: list[ContainerFactDefinition] = tablets_possible_containers

    def apply(self, world: World) -> None:
        statues_enter_text = (
            "Three weathered stone statues stand in a line beside the path: "
            "the statue to the left is a crouching lion, the middle statue is a "
            "eagle with spread wings, and the statue to the right is a towering bear."
        )
        world.add_definition(
            TriggerFunctionDefinition(
                MoveEventPattern("$from", self.statue_location.key),
                [
                    OnEventPrint(statues_enter_text, 20)
                ],
            )
        )

        lion_statue = ItemFactDefinition(
            key="lion_statue",
            name="Lion statue",
            text_pickup="",
            text_drop="",
            text_examine="A crouching lion carved in stone. There is one empty slot set in its chest.",
            text_enter="",
            text_look="The lion statue has one carved slot ready to hold something.",
            can_pickup=False,
        )
        world.add_definition(lion_statue)
        world.add_definition(
            StateWrapperDefinition(AtFactPattern(lion_statue.key, self.statue_location.key))
        )

        eagle_statue = ItemFactDefinition(
            key="eagle_statue",
            name="Eagle statue",
            text_pickup="",
            text_drop="",
            text_examine="An eagle with spread wings is sculpted from worn stone. There is one empty slot in its chest.",
            text_enter="",
            text_look="The eagle statue has one carved slot ready to hold something.",
            can_pickup=False,
        )
        world.add_definition(eagle_statue)
        world.add_definition(
            StateWrapperDefinition(AtFactPattern(eagle_statue.key, self.statue_location.key))
        )

        bear_statue = ItemFactDefinition(
            key="bear_statue",
            name="Bear statue",
            text_pickup="",
            text_drop="",
            text_examine="A broad bear statue stands on two legs, chipped by time. One empty slot is carved into its shoulder.",
            text_enter="",
            text_look="The bear statue has one carved slot ready to hold something.",
            can_pickup=False,
        )
        world.add_definition(bear_statue)
        world.add_definition(
            StateWrapperDefinition(AtFactPattern(bear_statue.key, self.statue_location.key))
        )

        selected_containers = random.sample(self.tablets_possible_containers, 3)
        tablets = [
            ("tablet_e", "Rock tablet E", "E"),
            ("tablet_g", "Rock tablet G", "G"),
            ("tablet_o", "Rock tablet O", "O"),
        ]
        for (tablet_key, tablet_name, letter), container in zip(
            tablets, selected_containers
        ):
            tablet = ItemFactDefinition(
                key=tablet_key,
                name=tablet_name,
                text_pickup=f"You pick up the rock tablet with the letter '{letter}'.",
                text_drop=f"You set down the rock tablet with the letter '{letter}'.",
                text_examine=f"A carved rock tablet marked with the letter '{letter}'.",
                text_enter="",
                text_look=f"A carved rock tablet marked with the letter '{letter}'.",
            )
            world.add_definition(tablet)
            world.add_definition(
                StateWrapperDefinition(AtFactPattern(tablet.key, container.key))
            )

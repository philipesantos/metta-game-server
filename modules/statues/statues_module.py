import random

from core.definitions.facts.container_fact_definition import ContainerFactDefinition
from core.definitions.facts.item_fact_definition import ItemFactDefinition
from core.definitions.facts.location_fact_definition import LocationFactDefinition
from core.definitions.functions.trigger_function_definition import (
    TriggerFunctionDefinition,
)
from core.definitions.side_effects.on_event_print import OnEventPrint
from core.definitions.wrappers.state_wrapper_definition import StateWrapperDefinition
from core.patterns.events.move_event_pattern import MoveEventPattern
from core.patterns.events.use_event_pattern import UseEventPattern
from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.patterns.facts.character_fact_pattern import CharacterFactPattern
from core.world import World
from modules.cave.cave_entrance_block import CaveEntranceBlock
from modules.module import Module
from modules.statues.functions.statues_helpers_function_definition import (
    StatuesHelpersFunctionDefinition,
)
from modules.statues.side_effects.statues_module_on_use_rune_on_statue import (
    StatuesModuleOnUseRuneOnStatue,
)


class StatuesModule(Module):
    def __init__(
        self,
        character: CharacterFactPattern,
        statue_location: LocationFactDefinition,
        runes_possible_containers: list[ContainerFactDefinition],
        fixed_rune_location_key: str | None = None,
        cave_entrance_block: CaveEntranceBlock | None = None,
    ):
        if len(runes_possible_containers) < 3:
            raise ValueError(
                "runes_possible_containers must contain at least 3 containers."
            )
        self.character: CharacterFactPattern = character
        self.statue_location: LocationFactDefinition = statue_location
        self.runes_possible_containers: list[ContainerFactDefinition] = (
            runes_possible_containers
        )
        self.fixed_rune_location_key = fixed_rune_location_key
        self.cave_entrance_block = cave_entrance_block

    def apply(self, world: World) -> None:
        statues_enter_text = (
            "Three weathered stone statues stand in a line beside the path: a lion "
            "statue, an eagle statue, and a bear statue, each with a narrow slot "
            "carved into its front."
        )
        world.add_definition(
            TriggerFunctionDefinition(
                MoveEventPattern("$from", self.statue_location.key),
                [OnEventPrint(statues_enter_text, 20)],
            )
        )
        world.add_definition(StatuesHelpersFunctionDefinition())

        lion_statue = ItemFactDefinition(
            key="lion_statue",
            name="Lion statue",
            text_pickup="",
            text_drop="",
            text_examine=(
                "The stone lion crouches low to the ground, worn smooth by time, "
                "with a narrow slot carved into its front."
            ),
            text_enter="",
            text_look="The lion statue has one carved slot ready to hold something.",
            can_pickup=False,
        )
        world.add_definition(lion_statue)
        world.add_definition(
            StateWrapperDefinition(
                AtFactPattern(lion_statue.key, self.statue_location.key)
            )
        )

        eagle_statue = ItemFactDefinition(
            key="eagle_statue",
            name="Eagle statue",
            text_pickup="",
            text_drop="",
            text_examine=(
                "The eagle's wings are spread wide in weathered stone, with a "
                "narrow slot carved into its front."
            ),
            text_enter="",
            text_look="The eagle statue has one carved slot ready to hold something.",
            can_pickup=False,
        )
        world.add_definition(eagle_statue)
        world.add_definition(
            StateWrapperDefinition(
                AtFactPattern(eagle_statue.key, self.statue_location.key)
            )
        )

        bear_statue = ItemFactDefinition(
            key="bear_statue",
            name="Bear statue",
            text_pickup="",
            text_drop="",
            text_examine=(
                "The broad bear statue rises on two legs, chipped by time, with a "
                "narrow slot carved into its front."
            ),
            text_enter="",
            text_look="The bear statue has one carved slot ready to hold something.",
            can_pickup=False,
        )
        world.add_definition(bear_statue)
        world.add_definition(
            StateWrapperDefinition(
                AtFactPattern(bear_statue.key, self.statue_location.key)
            )
        )

        statue_defs = (
            (lion_statue.key, "lion statue"),
            (eagle_statue.key, "eagle statue"),
            (bear_statue.key, "bear statue"),
        )

        selected_containers = random.sample(self.runes_possible_containers, 3)
        runes = [
            ("epsilon_rune", "Epsilon rune", "E", "epsilon"),
            ("gamma_rune", "Gamma rune", "G", "gamma"),
            ("omicron_rune", "Omicron rune", "O", "omicron"),
        ]
        for (rune_key, rune_name, letter, greek_name), container in zip(
            runes, selected_containers
        ):
            rune = ItemFactDefinition(
                key=rune_key,
                name=rune_name,
                text_pickup=f"You pick up the {greek_name} rune.",
                text_drop=f"You set down the {greek_name} rune.",
                text_examine=(
                    f"The carved {greek_name} rune is worn smooth at the edges and "
                    f"marked with the letter '{letter}'."
                ),
                text_enter=f"A {greek_name} rune rests here.",
                text_look=f"A {greek_name} rune rests inside.",
            )
            world.add_definition(rune)
            world.add_definition(
                StateWrapperDefinition(
                    AtFactPattern(
                        rune.key,
                        self.fixed_rune_location_key or container.key,
                    )
                )
            )
            for statue_key, statue_name in statue_defs:
                world.add_definition(
                    TriggerFunctionDefinition(
                        UseEventPattern(rune.key, statue_key),
                        [
                            StatuesModuleOnUseRuneOnStatue(
                                self.character,
                                rune.key,
                                rune_name.lower(),
                                statue_key,
                                statue_name,
                                self.cave_entrance_block,
                            )
                        ],
                    )
                )

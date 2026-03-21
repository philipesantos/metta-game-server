from core.definitions.facts.character_fact_definition import CharacterFactDefinition
from core.definitions.facts.container_fact_definition import ContainerFactDefinition
from core.definitions.facts.item_fact_definition import ItemFactDefinition
from core.definitions.facts.location_fact_definition import LocationFactDefinition
from core.definitions.facts.route_block_fact_definition import RouteBlockFactDefinition
from core.definitions.functions.trigger_function_definition import (
    TriggerFunctionDefinition,
)
from core.definitions.side_effects.on_event_print import OnEventPrint
from core.definitions.side_effects.on_use_combine_item import OnUseCombineItem
from core.definitions.wrappers.state_wrapper_definition import StateWrapperDefinition
from core.patterns.events.move_event_pattern import MoveEventPattern
from core.patterns.events.use_event_pattern import UseEventPattern
from core.patterns.events.use_item_event_pattern import UseItemEventPattern
from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.patterns.facts.character_fact_pattern import CharacterFactPattern
from core.world import World
from modules.module import Module
from modules.cave.functions.stay_still_function_definition import (
    StayStillFunctionDefinition,
)
from modules.cave.side_effects.cave_module_on_bear_encounter_arm_threat import (
    CaveModuleOnBearEncounterArmThreat,
)
from modules.cave.side_effects.cave_module_on_bear_threat_death import (
    CaveModuleOnBearThreatDeath,
)
from modules.cave.side_effects.cave_module_on_bear_threat_resolve_stay_still import (
    CaveModuleOnBearThreatResolveStayStill,
)
from modules.cave.side_effects.cave_module_on_stay_still_update_tick import (
    CaveModuleOnStayStillUpdateTick,
)
from modules.cave.side_effects.cave_module_on_enter_cave_describe import (
    CaveModuleOnEnterCaveDescribe,
)
from modules.cave.side_effects.cave_module_on_use_functioning_lantern import (
    CaveModuleOnUseFunctioningLantern,
)
from modules.cave.patterns.stay_still_event_pattern import StayStillEventPattern


class CaveModule(Module):
    def __init__(
        self,
        cave_entrance_location: LocationFactDefinition,
        character: CharacterFactPattern,
        lantern_container: ContainerFactDefinition | None = None,
        cave_items_to_reveal: list[ItemFactDefinition] | None = None,
    ):
        self.cave_entrance_location = cave_entrance_location
        self.character = character
        self.lantern_container = lantern_container
        self.cave_items_to_reveal = cave_items_to_reveal or []
        self.cave_location = LocationFactDefinition(
            key="cave",
            text_move_to="",
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
            text_examine=(
                "The boulder is immense, wedged deep into the entrance and far too "
                "heavy to shift by hand."
            ),
            text_enter="A massive boulder blocks the cave entrance here.",
            text_look="The rock is wedged tightly in place, completely sealing the path ahead.",
            can_pickup=False,
        )
        self.lantern = ItemFactDefinition(
            key="lantern",
            name="Lantern",
            text_enter="A weathered lantern rests here, dulled by dust and age.",
            text_examine=(
                "The lantern's glass is clouded and the reservoir is dry, but the frame "
                "itself is still intact."
            ),
            text_look="Inside, a weathered lantern lies in the chest.",
            text_drop="You drop the lantern.",
            text_pickup="You pick up the lantern.",
        )
        self.functioning_lantern = ItemFactDefinition(
            key="functioning_lantern",
            name="Lantern",
            text_pickup="You pick up the lantern.",
            text_drop="You drop the lantern.",
            text_examine=(
                "Fresh oil sloshes inside the weathered lantern, ready to feed a steady "
                "flame."
            ),
            text_enter="A lantern filled with fresh oil rests here.",
            text_look="Inside, a lantern filled with fresh oil rests in the chest.",
        )
        self.lantern_oil = ItemFactDefinition(
            key="oil",
            name="Lantern oil",
            text_enter="A small metal flask of lantern oil has been left here.",
            text_examine=(
                "The flask is sealed tight and filled with clear lamp oil that smells "
                "sharp and flammable."
            ),
            text_look="A small flask of lantern oil rests here.",
            text_drop="You set the lantern oil down.",
            text_pickup="You pick up the lantern oil.",
        )

    def apply(self, world: World) -> None:
        world.add_definition(StayStillFunctionDefinition(self.character))
        world.add_definition(
            TriggerFunctionDefinition(
                StayStillEventPattern("$where"),
                [
                    CaveModuleOnStayStillUpdateTick(),
                    CaveModuleOnBearThreatResolveStayStill(
                        self.character,
                        self.bear.key,
                        self.cave_location.key,
                        self.cave_items_to_reveal,
                    ),
                ],
            )
        )
        world.add_definition(
            TriggerFunctionDefinition(
                MoveEventPattern("$from", self.cave_location.key),
                [CaveModuleOnEnterCaveDescribe(self.cave_location.key)],
            )
        )
        world.add_definition(
            TriggerFunctionDefinition(
                MoveEventPattern("$from", self.cave_location.key),
                [
                    CaveModuleOnBearEncounterArmThreat(
                        self.character, self.bear.key, self.cave_location.key
                    )
                ],
            )
        )
        world.add_definition(
            TriggerFunctionDefinition(
                MoveEventPattern("$from", "$to"),
                [CaveModuleOnBearThreatDeath(self.character)],
            )
        )
        world.add_definition(self.cave_location)
        world.add_definition(self.bear)
        world.add_definition(self.boulder)
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
        world.add_definition(self.lantern_oil)
        if self.lantern_container is None:
            return
        world.add_definition(self.lantern)
        world.add_definition(self.functioning_lantern)
        world.add_definition(
            StateWrapperDefinition(
                AtFactPattern(self.lantern.key, self.lantern_container.key)
            )
        )
        world.add_definition(
            TriggerFunctionDefinition(
                UseEventPattern(self.lantern_oil.key, self.lantern.key),
                [
                    OnUseCombineItem(
                        self.lantern,
                        self.lantern_oil,
                        self.functioning_lantern,
                    ),
                    OnEventPrint(
                        "You pour the oil into the lantern. It is ready to use."
                    ),
                ],
            )
        )
        world.add_definition(
            TriggerFunctionDefinition(
                UseItemEventPattern(self.functioning_lantern.key),
                [
                    CaveModuleOnUseFunctioningLantern(
                        self.character,
                        self.cave_location.key,
                        self.bear.key,
                        self.cave_items_to_reveal,
                    )
                ],
            )
        )

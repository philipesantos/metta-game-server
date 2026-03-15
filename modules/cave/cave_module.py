from core.definitions.facts.character_fact_definition import CharacterFactDefinition
from core.definitions.facts.item_fact_definition import ItemFactDefinition
from core.definitions.facts.location_fact_definition import LocationFactDefinition
from core.definitions.facts.route_block_fact_definition import RouteBlockFactDefinition
from core.definitions.functions.trigger_function_definition import (
    TriggerFunctionDefinition,
)
from core.definitions.wrappers.state_wrapper_definition import StateWrapperDefinition
from core.patterns.events.move_event_pattern import MoveEventPattern
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
            key="cave",
            text_move_to=(
                "A cold cave opens into darkness, its stone walls swallowing what "
                "little light enters."
            ),
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

    def apply(self, world: World) -> None:
        world.add_definition(StayStillFunctionDefinition(self.character))
        world.add_definition(
            TriggerFunctionDefinition(
                StayStillEventPattern("$where"),
                [
                    CaveModuleOnBearThreatResolveStayStill(
                        self.character, self.bear.key, self.cave_location.key
                    ),
                    CaveModuleOnStayStillUpdateTick(),
                ],
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

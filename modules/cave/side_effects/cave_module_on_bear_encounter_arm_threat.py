from core.definitions.side_effect_definition import SideEffectDefinition
from core.patterns.events.move_event_pattern import MoveEventPattern
from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.patterns.facts.character_fact_pattern import CharacterFactPattern
from core.patterns.functions.exists_function_pattern import ExistsFunctionPattern
from core.patterns.wrappers.state_wrapper_pattern import StateWrapperPattern
from modules.cave.patterns.bear_threat_pending_fact_pattern import (
    BearThreatPendingFactPattern,
)


class CaveModuleOnBearEncounterArmThreat(SideEffectDefinition):
    def __init__(
        self,
        character: CharacterFactPattern,
        bear_key: str,
        bear_location: str,
    ):
        self.character = character
        self.bear_key = bear_key
        self.bear_location = bear_location

    def to_metta(self, event: MoveEventPattern) -> str:
        pending_state = StateWrapperPattern(
            BearThreatPendingFactPattern(self.character.key)
        )
        bear_state = StateWrapperPattern(
            AtFactPattern(self.bear_key, self.bear_location)
        )
        # fmt: off
        return (
            f"(if {ExistsFunctionPattern(bear_state).to_metta()}\n"
            f"    (if {ExistsFunctionPattern(pending_state).to_metta()}\n"
            f"        Empty\n"
            f"        (add-atom &self {pending_state.to_metta()})\n"
            f"    )\n"
            f"    Empty\n"
            f")\n"
        )
        # fmt: on

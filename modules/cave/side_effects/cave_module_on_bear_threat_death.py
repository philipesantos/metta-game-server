from core.definitions.side_effect_definition import SideEffectDefinition
from core.patterns.events.move_event_pattern import MoveEventPattern
from core.patterns.facts.character_fact_pattern import CharacterFactPattern
from core.patterns.facts.game_over_fact_pattern import GameOverFactPattern
from core.patterns.facts.response_fact_pattern import ResponseFactPattern
from core.patterns.functions.exists_function_pattern import ExistsFunctionPattern
from core.patterns.wrappers.state_wrapper_pattern import StateWrapperPattern
from modules.cave.patterns.bear_threat_pending_fact_pattern import (
    BearThreatPendingFactPattern,
)


class CaveModuleOnBearThreatDeath(SideEffectDefinition):
    def __init__(self, character: CharacterFactPattern):
        self.character = character

    def to_metta(self, event: MoveEventPattern) -> str:
        pending_state = StateWrapperPattern(
            BearThreatPendingFactPattern(self.character.key)
        )
        game_over_state = StateWrapperPattern(
            GameOverFactPattern(
                '"The bear lunges before you can react and tears you apart. You died."'
            )
        )
        death_message = ResponseFactPattern(
            200, '"The bear lunges before you can react and tears you apart. You died."'
        )
        # fmt: off
        return (
            f"(if {ExistsFunctionPattern(pending_state).to_metta()}\n"
            f"    (let* ((() (remove-atom &self {pending_state.to_metta()}))\n"
            f"           (() (add-atom &self {game_over_state.to_metta()})))\n"
            f"        {death_message.to_metta()}\n"
            f"    )\n"
            f"    Empty\n"
            f")\n"
        )
        # fmt: on

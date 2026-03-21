from core.definitions.side_effect_definition import SideEffectDefinition
from core.patterns.event_pattern import EventPattern
from core.patterns.facts.game_won_fact_pattern import GameWonFactPattern
from core.patterns.facts.response_fact_pattern import ResponseFactPattern
from core.patterns.wrappers.state_wrapper_pattern import StateWrapperPattern


class OnGameWon(SideEffectDefinition):
    def __init__(self, text: str):
        self.text = text

    def to_metta(self, event: EventPattern) -> str:
        game_won_state = StateWrapperPattern(GameWonFactPattern(self._quote(self.text)))
        win_message = ResponseFactPattern(200, self._quote(self.text))
        # fmt: off
        return (
            f"(let* ((() (add-atom &self {game_won_state.to_metta()})))\n"
            f"    {win_message.to_metta()}\n"
            f")\n"
        )
        # fmt: on

    @staticmethod
    def _quote(text: str) -> str:
        escaped = text.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'

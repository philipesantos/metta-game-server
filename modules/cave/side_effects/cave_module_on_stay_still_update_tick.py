from core.definitions.side_effect_definition import SideEffectDefinition
from core.patterns.wrappers.stale_wrapper_pattern import StaleWrapperPattern
from modules.cave.patterns.stay_still_event_pattern import StayStillEventPattern


class CaveModuleOnStayStillUpdateTick(SideEffectDefinition):
    def to_metta(self, event: StayStillEventPattern) -> str:
        stale_tick = StaleWrapperPattern("Tick")
        # fmt: off
        return (
            f"(if (exists {stale_tick.to_metta()})\n"
            f"    Empty\n"
            f"    (add-atom &self {stale_tick.to_metta()})\n"
            f")\n"
        )
        # fmt: on

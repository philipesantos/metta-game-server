from core.definitions.side_effect_definition import SideEffectDefinition
from core.patterns.events.move_event_pattern import MoveEventPattern
from core.patterns.facts.response_fact_pattern import ResponseFactPattern
from core.patterns.functions.exists_function_pattern import ExistsFunctionPattern
from core.patterns.wrappers.state_wrapper_pattern import StateWrapperPattern
from modules.cave.patterns.cave_lit_fact_pattern import CaveLitFactPattern


class CaveModuleOnEnterCaveDescribe(SideEffectDefinition):
    def __init__(self, cave_location: str):
        self.cave_location = cave_location

    def to_metta(self, event: MoveEventPattern) -> str:
        cave_lit_state = StateWrapperPattern(CaveLitFactPattern(self.cave_location))
        dark_message = ResponseFactPattern(
            120, '"The cave is pitch dark, and you cannot make out anything ahead."'
        )
        lit_message = ResponseFactPattern(
            120,
            '"The lantern light spills across damp stone walls and old bones scattered across the cave floor."',
        )
        # fmt: off
        return (
            f"(if {ExistsFunctionPattern(cave_lit_state).to_metta()}\n"
            f"    {lit_message.to_metta()}\n"
            f"    {dark_message.to_metta()}\n"
            f")\n"
        )
        # fmt: on

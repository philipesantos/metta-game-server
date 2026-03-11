from core.definitions.facts.item_fact_definition import ItemFactDefinition
from core.definitions.facts.container_fact_definition import ContainerFactDefinition
from core.definitions.side_effect_definition import SideEffectDefinition
from core.patterns.events.use_event_pattern import UseEventPattern
from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.patterns.wrappers.state_wrapper_pattern import StateWrapperPattern


class CabinModuleOnUseUnlock(SideEffectDefinition):
    def __init__(
        self,
        location_key: str,
        locked_cabin: ContainerFactDefinition,
        cabin: ContainerFactDefinition,
        metal_key: ItemFactDefinition,
    ):
        self.location_key = location_key
        self.locked_cabin = locked_cabin
        self.cabin = cabin
        self.metal_key = metal_key

    def to_metta(self, event: UseEventPattern) -> str:
        locked_cabin_state = StateWrapperPattern(AtFactPattern("cabin", self.location_key))
        cabin_state = StateWrapperPattern(AtFactPattern("cabin", self.location_key))
        metal_key_state = StateWrapperPattern(AtFactPattern(self.metal_key.key, "$key_where"))
        remove_locked_definition = "\n".join(
            f"    (() (remove-atom &self {expression}))"
            for expression in self._split_expressions(self.locked_cabin.to_metta())
        )
        add_cabin_definition = "\n".join(
            f"    (() (add-atom &self {expression}))"
            for expression in self._split_expressions(self.cabin.to_metta())
        )
        return (
            f"(let* (\n"
            f"{remove_locked_definition}\n"
            f"{add_cabin_definition}\n"
            f"    (() (remove-atom &self {locked_cabin_state.to_metta()}))\n"
            f"    (() (remove-atom &self {cabin_state.to_metta()}))\n"
            f"    (() (match &self {metal_key_state.to_metta()} (remove-atom &self {metal_key_state.to_metta()})))\n"
            f"    (() (add-atom &self {cabin_state.to_metta()}))\n"
            f")\n"
            f"    Empty\n"
            f")\n"
        )

    @staticmethod
    def _split_expressions(metta: str) -> list[str]:
        expressions: list[str] = []
        current: list[str] = []
        depth = 0
        in_string = False
        escaped = False

        for char in metta:
            if depth == 0 and char.isspace():
                continue

            current.append(char)

            if in_string:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    in_string = False
                continue

            if char == '"':
                in_string = True
            elif char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth == 0:
                    expressions.append("".join(current).strip())
                    current = []

        return expressions

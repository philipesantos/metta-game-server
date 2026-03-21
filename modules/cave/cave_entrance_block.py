from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.patterns.facts.route_block_fact_pattern import RouteBlockFactPattern
from core.patterns.wrappers.state_wrapper_pattern import StateWrapperPattern


class CaveEntranceBlock:
    def __init__(
        self,
        boulder_key: str,
        boulder_location: str,
        route_from: str,
        route_to: str,
        route_reason: str,
    ):
        self.boulder_key = boulder_key
        self.boulder_location = boulder_location
        self.route_from = route_from
        self.route_to = route_to
        self.route_reason = route_reason

    def boulder_state(self) -> StateWrapperPattern:
        return StateWrapperPattern(AtFactPattern(self.boulder_key, self.boulder_location))

    def route_block(self) -> RouteBlockFactPattern:
        return RouteBlockFactPattern(
            self.route_from,
            self.route_to,
            self.route_reason,
        )

    def removal_updates(self, indent: str = "                ") -> str:
        return (
            f"{indent}(() (remove-atom &self {self.boulder_state().to_metta()}))\n"
            f"{indent}(() (remove-atom &self {self.route_block().to_metta()}))\n"
        )

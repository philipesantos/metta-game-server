from core.definitions.fact_definition import FactDefinition
from core.patterns.facts.route_description_fact_pattern import (
    RouteDescriptionFactPattern,
)


class RouteDescriptionFactDefinition(FactDefinition):
    def __init__(
        self,
        location_from: str,
        direction: str,
        location_to: str,
        description: str,
    ):
        self.location_from = location_from
        self.direction = direction
        self.location_to = location_to
        self.description = description

    def to_metta(self) -> str:
        return RouteDescriptionFactPattern(
            self.location_from,
            self.direction,
            self.location_to,
            self.description,
        ).to_metta()

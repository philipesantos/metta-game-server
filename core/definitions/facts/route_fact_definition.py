from core.definitions.fact_definition import FactDefinition
from core.definitions.facts.route_description_fact_definition import (
    RouteDescriptionFactDefinition,
)
from core.patterns.facts.route_fact_pattern import RouteFactPattern


class RouteFactDefinition(FactDefinition):
    def __init__(
        self,
        location_from: str,
        direction: str,
        location_to: str,
        description: str | None = None,
    ):
        self.location_from = location_from
        self.direction = direction
        self.location_to = location_to
        self.description = description

    def to_metta(self) -> str:
        route = RouteFactPattern(
            self.location_from, self.direction, self.location_to
        ).to_metta()
        if self.description is None:
            return route

        route_description = RouteDescriptionFactDefinition(
            self.location_from,
            self.direction,
            self.location_to,
            self.description,
        ).to_metta()
        return f"{route}\n{route_description}"

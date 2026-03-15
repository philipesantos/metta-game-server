from core.patterns.fact_pattern import FactPattern
from utils.type import Type


class RouteDescriptionFactPattern(FactPattern):
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
        description = self._format_description()
        return (
            f'({Type.ROUTE_DESCRIPTION.value} {self.location_from} '
            f"{self.direction} {self.location_to} {description})"
        )

    def _format_description(self) -> str:
        if self.description.startswith("$"):
            return self.description
        if self.description.startswith('"') and self.description.endswith('"'):
            return self.description
        return f'"{self.description}"'

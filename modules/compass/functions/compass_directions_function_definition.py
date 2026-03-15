from core.definitions.function_definition import FunctionDefinition
from core.patterns.facts.route_description_fact_pattern import (
    RouteDescriptionFactPattern,
)
from core.patterns.facts.response_fact_pattern import ResponseFactPattern


class CompassDirectionsFunctionDefinition(FunctionDefinition):
    def to_metta(self) -> str:
        route_description = RouteDescriptionFactPattern(
            "$from",
            "$direction",
            "$to",
            "$description",
        )
        return (
            f"(= (compass-directions ($from))\n"
            f"    (match &self {route_description.to_metta()}\n"
            f"        {ResponseFactPattern(5, '$description').to_metta()}\n"
            f"    )\n"
            f")"
        )

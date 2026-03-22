from core.definitions.function_definition import FunctionDefinition
from core.patterns.facts.route_block_fact_pattern import RouteBlockFactPattern
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
        route_block = RouteBlockFactPattern("$from", "$to", "$reason")
        return (
            f"(= (compass-directions ($from))\n"
            f"    (match &self {route_description.to_metta()}\n"
            f"        (case (match &self {route_block.to_metta()} $reason)\n"
            f"        (\n"
            f"            (Empty {ResponseFactPattern(5, '$description').to_metta()})\n"
            f"            ($reason Empty)\n"
            f"        ))\n"
            f"    )\n"
            f")"
        )

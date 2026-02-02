from core.definitions.function_definition import FunctionDefinition
from core.patterns.facts.route_fact_pattern import RouteFactPattern
from core.patterns.facts.response_fact_pattern import ResponseFactPattern


class CompassDirectionsFunctionDefinition(FunctionDefinition):
    def to_metta(self) -> str:
        route = RouteFactPattern("$from", "$direction", "$_")
        # fmt: off
        return (
            f"(= (compass-directions ($from))\n"
            f"    {ResponseFactPattern(10, f'("You can go: " (collapse (match &self {route.to_metta()} $direction)))').to_metta()}\n"
            f")"
        )
        # fmt: on

from core.definitions.side_effect_definition import SideEffectDefinition
from core.patterns.events.pickup_event_pattern import PickUpEventPattern
from core.patterns.facts.route_block_fact_pattern import RouteBlockFactPattern


class CompassModuleOnPickupRemoveRouteBlocks(SideEffectDefinition):
    def __init__(self, location_from: str):
        self.location_from = location_from

    def to_metta(self, event: PickUpEventPattern) -> str:
        route_block_match = RouteBlockFactPattern(self.location_from, "$to", "$reason")
        # fmt: off
        return (
            f"(let* ((() (match &self {route_block_match.to_metta()}\n"
            f"    (remove-atom &self {route_block_match.to_metta()}))))\n"
            f"    Empty\n"
            f")\n"
        )
        # fmt: on

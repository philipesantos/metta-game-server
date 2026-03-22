from core.definitions.side_effect_definition import SideEffectDefinition
from core.patterns.events.pickup_event_pattern import PickUpEventPattern
from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.patterns.facts.character_fact_pattern import CharacterFactPattern
from core.patterns.facts.route_block_fact_pattern import RouteBlockFactPattern
from core.patterns.wrappers.state_wrapper_pattern import StateWrapperPattern
from modules.compass.patterns.compass_directions_function_pattern import (
    CompassDirectionsFunctionPattern,
)


class CompassModuleOnPickupPrintDirections(SideEffectDefinition):
    def __init__(
        self,
        character: CharacterFactPattern,
        unblock_location_from: str | None = None,
    ):
        self.character = character
        self.unblock_location_from = unblock_location_from

    def to_metta(self, event: PickUpEventPattern) -> str:
        state_at_player = StateWrapperPattern(
            AtFactPattern(self.character.key, "$player_where")
        )
        directions = CompassDirectionsFunctionPattern("$player_where")
        unblock_updates = self._unblock_updates()
        # fmt: off
        return (
            f"(let* (\n"
            f"{unblock_updates}"
            f"    ($player_where (match &self {state_at_player.to_metta()} $player_where))\n"
            f")\n"
            f"    {directions.to_metta()}\n"
            f")"
        )
        # fmt: on

    def _unblock_updates(self) -> str:
        if self.unblock_location_from is None:
            return ""

        route_block_match = RouteBlockFactPattern(
            self.unblock_location_from, "$to", "$reason"
        )
        return (
            f"    ($unblocked (collapse (match &self {route_block_match.to_metta()}\n"
            f"        (remove-atom &self {route_block_match.to_metta()}))))\n"
        )

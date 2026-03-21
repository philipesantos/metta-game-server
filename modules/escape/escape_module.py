import random

from core.definitions.functions.trigger_function_definition import (
    TriggerFunctionDefinition,
)
from core.definitions.facts.item_fact_definition import ItemFactDefinition
from core.definitions.facts.location_fact_definition import LocationFactDefinition
from core.definitions.side_effects.on_game_won import OnGameWon
from core.definitions.wrappers.state_wrapper_definition import StateWrapperDefinition
from core.patterns.events.use_event_pattern import UseEventPattern
from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.world import World
from modules.module import Module


class EscapeModule(Module):
    def __init__(
        self,
        boat_location: LocationFactDefinition,
        plane_location: LocationFactDefinition,
    ):
        self.boat_location = boat_location
        self.plane_location = plane_location
        self.propeller = ItemFactDefinition(
            key="propeller",
            name="Propeller",
            text_enter="A metal propeller lies here, green with age and salt.",
            text_examine=(
                "The propeller is scarred and tarnished, but its blades are still sound."
            ),
            text_look="A metal propeller is wedged here behind the falling water.",
            text_drop="You set the propeller down.",
            text_pickup="You pick up the propeller.",
        )
        self.battery = ItemFactDefinition(
            key="battery",
            name="Battery",
            text_enter="A heavy battery rests here, its metal casing dulled with age.",
            text_examine=(
                "The battery is scratched and worn, but the terminals are intact and it "
                "still feels charged."
            ),
            text_look="A heavy battery has been tucked away here.",
            text_drop="You set the battery down.",
            text_pickup="You pick up the battery.",
        )
        self.cave_item = random.choice([self.propeller, self.battery])
        if self.cave_item.key == self.propeller.key:
            self.boat = ItemFactDefinition(
                key="boat",
                name="Boat",
                text_pickup="",
                text_drop="",
                text_examine=(
                    "The boat's motor sits open and bare where the propeller should be, "
                    "but the rest of the boat still looks sound enough to carry you away."
                ),
                text_enter=(
                    "A small weathered boat rocks near the shore, its motor stripped of "
                    "its propeller."
                ),
                text_look=(
                    "The boat looks seaworthy, but the boat's motor cannot do anything "
                    "without a propeller."
                ),
                can_pickup=False,
            )
            self.plane = ItemFactDefinition(
                key="plane",
                name="Plane",
                text_pickup="",
                text_drop="",
                text_examine=(
                    "The plane's fuselage is split open and the frame is twisted beyond "
                    "any hope of repair."
                ),
                text_enter=(
                    "A ruined plane lies tangled among the trees, its frame broken beyond repair."
                ),
                text_look=(
                    "This plane is too badly broken to ever leave the ground again."
                ),
                can_pickup=False,
            )
        else:
            self.boat = ItemFactDefinition(
                key="boat",
                name="Boat",
                text_pickup="",
                text_drop="",
                text_examine=(
                    "The boat's hull is split and the engine housing is cracked clean "
                    "through. No part of the boat looks worth saving."
                ),
                text_enter=(
                    "A wrecked boat lies half-drawn onto the shore, too badly damaged to use."
                ),
                text_look=(
                    "The boat is beyond repair, little more than driftwood and rust."
                ),
                can_pickup=False,
            )
            self.plane = ItemFactDefinition(
                key="plane",
                name="Plane",
                text_pickup="",
                text_drop="",
                text_examine=(
                    "The plane's cockpit is intact, and the battery compartment hangs "
                    "open as if someone pulled the power source out long ago."
                ),
                text_enter=(
                    "A broken plane rests among the trees, its battery compartment standing open."
                ),
                text_look=(
                    "The plane is crippled, but the open battery compartment suggests it "
                    "might still be brought back to life."
                ),
                can_pickup=False,
            )

    def get_item(self) -> ItemFactDefinition:
        return self.cave_item

    def apply(self, world: World) -> None:
        world.add_definition(self.boat)
        world.add_definition(self.plane)
        world.add_definition(self.propeller)
        world.add_definition(self.battery)
        world.add_definition(
            StateWrapperDefinition(AtFactPattern(self.boat.key, self.boat_location.key))
        )
        world.add_definition(
            StateWrapperDefinition(
                AtFactPattern(self.plane.key, self.plane_location.key)
            )
        )
        world.add_definition(
            TriggerFunctionDefinition(
                UseEventPattern(self.propeller.key, self.boat.key),
                [
                    OnGameWon(
                        "You fit the propeller onto the boat's motor. The engine catches, "
                        "and you steer out across the water toward freedom."
                    )
                ],
            )
        )
        world.add_definition(
            TriggerFunctionDefinition(
                UseEventPattern(self.battery.key, self.plane.key),
                [
                    OnGameWon(
                        "You secure the battery in place. The dead controls shudder back "
                        "to life, and the plane carries you away from the island."
                    )
                ],
            )
        )
        if self.cave_item.key != self.propeller.key:
            world.add_definition(
                StateWrapperDefinition(AtFactPattern(self.propeller.key, "waterfall"))
            )
        if self.cave_item.key != self.battery.key:
            world.add_definition(
                StateWrapperDefinition(AtFactPattern(self.battery.key, "loose_board"))
            )

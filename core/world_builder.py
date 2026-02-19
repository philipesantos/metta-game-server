from core.definitions.facts.character_fact_definition import CharacterFactDefinition
from core.definitions.facts.location_fact_definition import LocationFactDefinition
from core.definitions.facts.route_fact_definition import RouteFactDefinition
from core.definitions.functions.drop_function_definition import DropFunctionDefinition
from core.definitions.functions.examine_function_definition import (
    ExamineFunctionDefinition,
)
from core.definitions.functions.exists_function_definition import (
    ExistsFunctionDefinition,
)
from core.definitions.functions.first_function_definition import FirstFunctionDefinition
from core.definitions.functions.inventory_function_definition import (
    InventoryFunctionPattern as InventoryFunctionDefinition,
)
from core.definitions.functions.last_function_definition import LastFunctionDefinition
from core.definitions.functions.location_path_function_definition import (
    LocationPathFunctionDefinition,
)
from core.definitions.functions.move_to_function_definition import (
    MoveToFunctionDefinition,
)
from core.definitions.functions.move_towards_function_definition import (
    MoveTowardsFunctionDefinition,
)
from core.definitions.functions.pickup_function_definition import (
    PickUpFunctionDefinition,
)
from core.definitions.functions.synchronize_tick_function_definition import (
    SynchronizeTickFunctionDefinition,
)
from core.definitions.functions.text_function_definition import TextFunctionDefinition
from core.definitions.functions.trigger_function_definition import (
    TriggerFunctionDefinition,
)
from core.definitions.functions.use_function_definition import UseFunctionDefinition
from core.definitions.side_effects.on_drop_update_at import OnDropUpdateAt
from core.definitions.side_effects.on_event_print import OnEventPrint
from core.definitions.side_effects.on_move_show_items import OnMoveShowItems
from core.definitions.side_effects.on_move_update_at import OnMoveUpdateAt
from core.definitions.side_effects.on_move_update_tick import OnMoveUpdateTick
from core.definitions.side_effects.on_pickup_update_at import OnPickUpUpdateAt
from core.definitions.side_effects.on_startup_show_items import OnStartupShowItems
from core.definitions.side_effects.on_use_do_nothing import OnUseDoNothing
from core.definitions.wrappers.state_wrapper_definition import StateWrapperDefinition
from core.patterns.events.drop_event_pattern import DropEventPattern
from core.patterns.events.move_event_pattern import MoveEventPattern
from core.patterns.events.pickup_event_pattern import PickUpEventPattern
from core.patterns.events.startup_event_pattern import StartupEventPattern
from core.patterns.events.use_event_pattern import UseEventPattern
from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.patterns.facts.tick_fact_pattern import TickFactPattern
from core.world import World
from modules.cave_entrance.cave_entrance_module import CaveEntranceModule
from modules.compass.compass_module import CompassModule
from utils.direction import Direction


def build_world() -> World:
    character_player = CharacterFactDefinition(key="player", name="John")

    location_glade = LocationFactDefinition(
        key="glade", text_move_to="You are in the Glade."
    )
    location_cave = LocationFactDefinition(
        key="cave", text_move_to="You are in the cave."
    )
    location_boat = LocationFactDefinition(
        key="boat", text_move_to="You are in the boat."
    )
    location_plane = LocationFactDefinition(
        key="plane", text_move_to="You are in the plane."
    )
    location_cabin = LocationFactDefinition(
        key="cabin", text_move_to="You are in the cabin."
    )
    location_camping_site = LocationFactDefinition(
        key="camping_site", text_move_to="You are in the camping site."
    )
    location_monolith = LocationFactDefinition(
        key="monolith", text_move_to="You are in the monolith."
    )
    location_path_1 = LocationFactDefinition(
        key="path_1", text_move_to="You are in the path 1."
    )
    location_path_2 = LocationFactDefinition(
        key="path_2", text_move_to="You are in the path 2."
    )
    location_path_3 = LocationFactDefinition(
        key="path_3", text_move_to="You are in the path 3."
    )
    location_path_4 = LocationFactDefinition(
        key="path_4", text_move_to="You are in the path 4."
    )
    location_path_5 = LocationFactDefinition(
        key="path_5", text_move_to="You are in the path 5."
    )
    location_path_6 = LocationFactDefinition(
        key="path_6", text_move_to="You are in the path 6."
    )
    location_path_7 = LocationFactDefinition(
        key="path_7", text_move_to="You are in the path 7."
    )
    location_path_8 = LocationFactDefinition(
        key="path_8", text_move_to="You are in the path 8."
    )
    location_path_9 = LocationFactDefinition(
        key="path_9", text_move_to="You are in the path 9."
    )

    world = World()

    world.add_definition(ExistsFunctionDefinition())
    world.add_definition(FirstFunctionDefinition())
    world.add_definition(LastFunctionDefinition())
    world.add_definition(TextFunctionDefinition())
    world.add_definition(LocationPathFunctionDefinition())
    world.add_definition(InventoryFunctionDefinition(character_player.to_pattern()))
    world.add_definition(MoveToFunctionDefinition(character_player.to_pattern()))
    world.add_definition(MoveTowardsFunctionDefinition(character_player.to_pattern()))
    world.add_definition(PickUpFunctionDefinition(character_player.to_pattern()))
    world.add_definition(DropFunctionDefinition(character_player.to_pattern()))
    world.add_definition(ExamineFunctionDefinition(character_player.to_pattern()))
    world.add_definition(UseFunctionDefinition(character_player.to_pattern()))
    world.add_definition(SynchronizeTickFunctionDefinition())

    world.add_definition(
        TriggerFunctionDefinition(
            MoveEventPattern("$from", "$to"),
            [
                OnMoveUpdateAt(character_player.to_pattern()),
                OnMoveUpdateTick(),
                OnMoveShowItems(),
            ],
        )
    )
    world.add_definition(
        TriggerFunctionDefinition(
            PickUpEventPattern("$what", "$where"),
            [OnPickUpUpdateAt(character_player.to_pattern())],
        )
    )
    world.add_definition(
        TriggerFunctionDefinition(
            DropEventPattern("$what", "$where"),
            [OnDropUpdateAt(character_player.to_pattern())],
        )
    )
    world.add_definition(
        TriggerFunctionDefinition(
            UseEventPattern("$what", "$with_what"),
            [OnUseDoNothing()],
        )
    )
    world.add_definition(
        TriggerFunctionDefinition(
            StartupEventPattern(),
            [
                OnEventPrint("You awaken in a glade."),
                OnStartupShowItems(character_player.to_pattern()),
            ],
        )
    )

    world.add_definition(character_player)

    world.add_definition(location_glade)
    world.add_definition(location_cave)
    world.add_definition(location_boat)
    world.add_definition(location_plane)
    world.add_definition(location_cabin)
    world.add_definition(location_camping_site)
    world.add_definition(location_monolith)
    world.add_definition(location_path_1)
    world.add_definition(location_path_2)
    world.add_definition(location_path_3)
    world.add_definition(location_path_4)
    world.add_definition(location_path_5)
    world.add_definition(location_path_6)
    world.add_definition(location_path_7)
    world.add_definition(location_path_8)
    world.add_definition(location_path_9)

    add_route(world, location_glade, Direction.SOUTH, location_path_1)
    add_route(world, location_path_1, Direction.WEST, location_path_2)
    add_route(world, location_path_2, Direction.SOUTH, location_cave)
    add_route(world, location_path_1, Direction.EAST, location_path_3)
    add_route(world, location_path_3, Direction.EAST, location_boat)
    add_route(world, location_glade, Direction.WEST, location_path_9)
    add_route(world, location_path_9, Direction.WEST, location_monolith)
    add_route(world, location_glade, Direction.NORTH, location_path_4)
    add_route(world, location_path_4, Direction.NORTH, location_path_5)
    add_route(world, location_path_5, Direction.EAST, location_path_6)
    add_route(world, location_path_6, Direction.EAST, location_plane)
    add_route(world, location_path_5, Direction.NORTH, location_path_7)
    add_route(world, location_path_7, Direction.WEST, location_path_8)
    add_route(world, location_path_8, Direction.WEST, location_cabin)
    add_route(world, location_path_7, Direction.NORTH, location_camping_site)

    world.add_definition(
        StateWrapperDefinition(AtFactPattern(character_player.key, location_glade.key))
    )

    world.add_definition(StateWrapperDefinition(TickFactPattern("1")))

    CompassModule(character_player.to_pattern(), location_glade.key).apply(world)
    CaveEntranceModule(location_path_2.key, location_cave.key).apply(world)

    return world


def add_route(
    world: World,
    location_from: LocationFactDefinition,
    direction: Direction,
    locations_to: LocationFactDefinition,
):
    world.add_definition(
        RouteFactDefinition(location_from.key, direction.value, locations_to.key)
    )
    world.add_definition(
        RouteFactDefinition(
            locations_to.key, direction.opposite.value, location_from.key
        )
    )

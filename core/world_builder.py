from core.definitions.facts.character_fact_definition import CharacterFactDefinition
from core.definitions.facts.container_fact_definition import ContainerFactDefinition
from core.definitions.facts.item_fact_definition import ItemFactDefinition
from core.definitions.facts.location_fact_definition import LocationFactDefinition
from core.definitions.facts.route_block_fact_definition import RouteBlockFactDefinition
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
from core.definitions.functions.look_in_function_definition import (
    LookInFunctionDefinition,
)
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
from core.definitions.side_effects.on_look_in_show_items import OnLookInShowItems
from core.definitions.side_effects.on_startup_show_items import OnStartupShowItems
from core.definitions.side_effects.on_use_do_nothing import OnUseDoNothing
from core.definitions.side_effects.on_use_combine_item import OnUseCombineItem
from core.definitions.wrappers.state_wrapper_definition import StateWrapperDefinition
from core.patterns.events.drop_event_pattern import DropEventPattern
from core.patterns.events.move_event_pattern import MoveEventPattern
from core.patterns.events.pickup_event_pattern import PickUpEventPattern
from core.patterns.events.startup_event_pattern import StartupEventPattern
from core.patterns.events.use_event_pattern import UseEventPattern
from core.patterns.events.look_in_event_pattern import LookInEventPattern
from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.patterns.facts.tick_fact_pattern import TickFactPattern
from core.world import World
from modules.cabin.cabin_module import CabinModule
from modules.compass.compass_module import CompassModule
from modules.statues.statues_module import StatuesModule
from utils.direction import Direction


def build_world() -> World:
    character_player = CharacterFactDefinition(key="player", name="John")

    location_glade = LocationFactDefinition(
        key="glade", text_move_to="You are in the glade."
    )
    location_cave = LocationFactDefinition(
        key="cave", text_move_to="You are in the cave."
    )
    location_beach = LocationFactDefinition(
        key="beach", text_move_to="You are in the beach."
    )
    location_boat = LocationFactDefinition(
        key="boat", text_move_to="You are in the boat."
    )
    location_plane = LocationFactDefinition(
        key="plane", text_move_to="You are in the plane."
    )
    location_camping_site = LocationFactDefinition(
        key="camping_site", text_move_to="You are in the camping site."
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
    world.add_definition(LookInFunctionDefinition(character_player.to_pattern()))
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
            LookInEventPattern("$container"),
            [OnLookInShowItems()],
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
    world.add_definition(location_beach)
    world.add_definition(location_boat)
    world.add_definition(location_plane)
    world.add_definition(location_camping_site)
    world.add_definition(location_path_1)
    world.add_definition(location_path_2)
    world.add_definition(location_path_3)
    world.add_definition(location_path_4)
    world.add_definition(location_path_5)

    add_route(world, location_glade, Direction.NORTH, location_path_1)
    add_route(world, location_path_1, Direction.NORTH, location_cave)
    add_route(world, location_glade, Direction.EAST, location_path_2)
    add_route(world, location_path_2, Direction.EAST, location_beach)
    add_route(world, location_beach, Direction.NORTH, location_boat)
    add_route(world, location_glade, Direction.SOUTH, location_path_3)
    add_route(world, location_path_3, Direction.EAST, location_plane)
    add_route(world, location_path_3, Direction.SOUTH, location_path_4)
    add_route(world, location_path_4, Direction.WEST, location_path_5)
    add_route(world, location_path_4, Direction.SOUTH, location_camping_site)

    world.add_definition(
        StateWrapperDefinition(AtFactPattern(character_player.key, location_glade.key))
    )

    disturbed_soil = ItemFactDefinition(
        key="disturbed_soil",
        name="Disturbed soil",
        text_pickup="",
        text_drop="",
        text_examine="The soil looks recently turned. It could hide something underneath.",
        text_enter="A patch of disturbed soil stands out beside the trail.",
        text_look="The disturbed soil is loose and shallow.",
        can_pickup=False,
    )
    world.add_definition(disturbed_soil)
    world.add_definition(
        StateWrapperDefinition(AtFactPattern(disturbed_soil.key, location_path_2.key))
    )

    huge_rock = ItemFactDefinition(
        key="huge_rock",
        name="Huge rock",
        text_pickup="",
        text_drop="",
        text_examine="A massive boulder blocks the cave entrance. You cannot move it by hand.",
        text_enter="A cave entrance is here, but a huge rock blocks it.",
        text_look="The rock is wedged tightly in place, completely sealing the path ahead.",
        can_pickup=False,
    )
    world.add_definition(huge_rock)
    world.add_definition(
        StateWrapperDefinition(AtFactPattern(huge_rock.key, location_path_1.key))
    )
    world.add_definition(
        RouteBlockFactDefinition(
            location_path_1.key,
            location_cave.key,
            "A huge rock blocks the cave entrance.",
        )
    )

    iron_box = ItemFactDefinition(
        key="iron_box",
        name="Iron box",
        text_pickup="You pick up the iron box.",
        text_drop="You drop the iron box.",
        text_examine="A small iron box, worn by time but still tightly sealed.",
        text_enter="A small iron box lies half-buried in fresh soil.",
        text_look="Inside, a small iron box is wedged in the dirt.",
    )
    world.add_definition(iron_box)

    container_hollow_tree_trunk = ContainerFactDefinition(
        key="tree_trunk",
        name="Hollow tree trunk",
        text_enter="An old tree trunk",
        text_examine="The tree trunk looks hollow",
        text_look="You put your hand inside the tree trunk.",
        text_contents="An old hollow tree trunk stands nearby.",
    )
    world.add_definition(container_hollow_tree_trunk)
    world.add_definition(
        StateWrapperDefinition(
            AtFactPattern(container_hollow_tree_trunk.key, location_path_3.key)
        )
    )

    container_rock_formation = ContainerFactDefinition(
        key="rock_formation",
        name="Suspicious rock formation",
        text_enter="A suspicious rock formation",
        text_examine="The rock formation doesn’t look natural. There seems to be a gap between the rocks.",
        text_look="You look inside the gap between the rocks.",
        text_contents="A suspicious rock formation has a narrow gap between the rocks.",
    )
    world.add_definition(container_rock_formation)
    world.add_definition(
        StateWrapperDefinition(
            AtFactPattern(container_rock_formation.key, location_path_4.key)
        )
    )

    big_chest = ContainerFactDefinition(
        key="chest",
        name="Big chest",
        text_enter="There is a chest near a tent",
        text_examine="It is a big chest, it looks open.",
        text_look="You look inside the chest.",
        text_contents="A big chest sits near the tent.",
    )
    world.add_definition(big_chest)
    world.add_definition(
        StateWrapperDefinition(AtFactPattern(big_chest.key, location_camping_site.key))
    )

    shovel = ItemFactDefinition(
        key="shovel",
        name="Shovel",
        text_enter="You see an old shovel.",
        text_examine="An old shovel, but it still looks sturdy enough to do the job.",
        text_look="Inside, an old shovel leans against the chest wall.",
        text_drop="You drop the old shovel.",
        text_pickup="You pick up the old shovel.",
    )
    world.add_definition(shovel)
    world.add_definition(
        StateWrapperDefinition(AtFactPattern(shovel.key, big_chest.key))
    )
    world.add_definition(
        TriggerFunctionDefinition(
            UseEventPattern(shovel.key, disturbed_soil.key),
            [
                OnEventPrint(
                    "You dig into the disturbed soil and uncover a small iron box."
                ),
                OnUseCombineItem(
                    disturbed_soil,
                    shovel,
                    iron_box,
                ),
            ],
        )
    )

    lantern = ItemFactDefinition(
        key="lantern",
        name="Lantern",
        text_enter="You see a weathered lantern.",
        text_examine="A weathered lantern. The oil inside has long since dried.",
        text_look="Inside, a weathered lantern lies in the chest.",
        text_drop="You drop the lantern.",
        text_pickup="You pick up the lantern.",
    )
    world.add_definition(lantern)
    world.add_definition(
        StateWrapperDefinition(AtFactPattern(lantern.key, big_chest.key))
    )

    functioning_lantern = ItemFactDefinition(
        key="functioning_lantern",
        name="Lantern",
        text_pickup="You pick up the lantern.",
        text_drop="You drop the lantern.",
        text_examine="A weathered lantern filled with fresh oil. It is ready to be lit.",
        text_enter="You see a lantern filled with fresh oil.",
        text_look="Inside, a lantern filled with fresh oil rests in the chest.",
    )
    world.add_definition(functioning_lantern)

    abandoned_well = ContainerFactDefinition(
        key="well",
        name="Abandoned well",
        text_enter="You see a abandoned well.",
        text_examine="A worn bucket sits inside, but the well seems dry.",
        text_look="You look inside the well.",
        text_contents="An abandoned well stands here.",
    )
    world.add_definition(abandoned_well)
    world.add_definition(
        StateWrapperDefinition(AtFactPattern(abandoned_well.key, location_path_5.key))
    )

    bucket = ContainerFactDefinition(
        key="bucket",
        name="Bucket",
        text_enter="A worn bucket rests here.",
        text_examine="An old wooden bucket with a frayed rope handle.",
        text_look="You peer into the bucket.",
        text_contents="A worn bucket hangs inside the well.",
    )
    world.add_definition(bucket)
    world.add_definition(
        StateWrapperDefinition(AtFactPattern(bucket.key, abandoned_well.key))
    )

    seashell = ContainerFactDefinition(
        key="seashell",
        name="Seashell",
        text_enter="A small seashell rests in the sand.",
        text_examine="Its surface is smooth and pale, shaped by the tide. The shell is slightly open, just enough to slip something inside.",
        text_look="You gently pry the shell open and look inside.",
        text_contents="A small seashell rests in the sand.",
    )
    world.add_definition(seashell)
    world.add_definition(
        StateWrapperDefinition(AtFactPattern(seashell.key, location_beach.key))
    )

    waterfall = ContainerFactDefinition(
        key="waterfall",
        name="Waterfall",
        text_enter="A narrow waterfall spills down the rocks beside the beach.",
        text_examine="Cold water cascades over the rock face and disappears into a shallow pool.",
        text_look="You peer through the falling water.",
        text_contents="A narrow waterfall spills down the rocks beside the beach.",
    )
    world.add_definition(waterfall)
    world.add_definition(
        StateWrapperDefinition(AtFactPattern(waterfall.key, location_beach.key))
    )

    lantern_oil = ItemFactDefinition(
        key="oil",
        name="Lantern oil",
        text_enter="You see a small metal flask filled with oil.",
        text_examine="A sealed flask containing clear lamp oil. It smells sharp and flammable.",
        text_look="A small flask of lantern oil rests here.",
        text_drop="You set the lantern oil down.",
        text_pickup="You pick up the lantern oil.",
    )

    world.add_definition(lantern_oil)
    world.add_definition(
        TriggerFunctionDefinition(
            UseEventPattern(lantern_oil.key, lantern.key),
            [
                OnUseCombineItem(lantern, lantern_oil, functioning_lantern),
                OnEventPrint("You pour the oil into the lantern. It is ready to use."),
            ],
        )
    )

    CompassModule(character_player.to_pattern(), location_glade).apply(world)
    CabinModule(
        location_path_5,
        seashell,
        [lantern_oil],
    ).apply(world)
    StatuesModule(
        character_player.to_pattern(),
        location_path_1,
        [
            container_hollow_tree_trunk,
            container_rock_formation,
            big_chest,
            bucket,
        ],
    ).apply(world)

    world.add_definition(StateWrapperDefinition(TickFactPattern("1")))

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

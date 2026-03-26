from core.definitions.facts.character_fact_definition import CharacterFactDefinition
from core.definitions.facts.container_fact_definition import ContainerFactDefinition
from core.definitions.facts.item_fact_definition import ItemFactDefinition
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
from core.definitions.functions.use_item_function_definition import (
    UseItemFunctionDefinition,
)
from core.definitions.side_effects.on_drop_update_at import OnDropUpdateAt
from core.definitions.side_effects.on_event_print import OnEventPrint
from core.definitions.side_effects.on_move_show_enter_text import (
    OnMoveShowEnterText,
)
from core.definitions.side_effects.on_move_update_at import OnMoveUpdateAt
from core.definitions.side_effects.on_move_update_tick import OnMoveUpdateTick
from core.definitions.side_effects.on_pickup_update_at import OnPickUpUpdateAt
from core.definitions.side_effects.on_look_in_show_items import OnLookInShowItems
from core.definitions.side_effects.on_startup_show_enter_text import (
    OnStartupShowEnterText,
)
from core.definitions.side_effects.on_use_item_fallback_print import (
    OnUseItemFallbackPrint,
)
from core.definitions.side_effects.on_use_combine_item import OnUseCombineItem
from core.definitions.side_effects.on_use_fallback_print import OnUseFallbackPrint
from core.definitions.wrappers.state_wrapper_definition import StateWrapperDefinition
from core.patterns.events.drop_event_pattern import DropEventPattern
from core.patterns.events.move_event_pattern import MoveEventPattern
from core.patterns.events.pickup_event_pattern import PickUpEventPattern
from core.patterns.events.startup_event_pattern import StartupEventPattern
from core.patterns.events.use_item_event_pattern import UseItemEventPattern
from core.patterns.events.use_event_pattern import UseEventPattern
from core.patterns.events.look_in_event_pattern import LookInEventPattern
from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.patterns.facts.tick_fact_pattern import TickFactPattern
from core.world import World
from modules.cabin.cabin_module import CabinModule
from modules.cave.cave_module import CaveModule
from modules.compass.compass_module import CompassModule
from modules.escape.escape_module import EscapeModule
from modules.statues.statues_module import StatuesModule
from utils.direction import Direction


def build_world() -> World:
    character_player = CharacterFactDefinition(key="player", name="John")

    location_glade = LocationFactDefinition(
        key="glade",
        text_move_to=(
            "A quiet glade opens beneath ancient trees, its grass bright with "
            "scattered wildflowers."
        ),
    )
    location_beach = LocationFactDefinition(
        key="beach",
        text_move_to=(
            "A broad beach of pale sand lies beneath dark rock beside the restless "
            "water."
        ),
    )
    location_camping_site = LocationFactDefinition(
        key="camping_site",
        text_move_to=(
            "An abandoned campsite lies beneath the trees, marked by flattened earth "
            "and a ring of ash."
        ),
    )
    location_ridge = LocationFactDefinition(
        key="ridge",
        text_move_to=(
            "A narrow ridge of pale stone rises above the glade, open to wind and sky."
        ),
    )
    location_shore_path = LocationFactDefinition(
        key="shore_path",
        text_move_to=(
            "A sandy trail descends toward the shore, where the air tastes of salt "
            "and spray."
        ),
    )
    location_forest_path = LocationFactDefinition(
        key="forest_path",
        text_move_to=(
            "A dim forest trail winds between tall trunks over ground soft with old "
            "needles."
        ),
    )
    location_plane_site = LocationFactDefinition(
        key="plane_site",
        text_move_to=(
            "The trees thin around a scar of torn earth and broken branches where "
            "something large came down hard."
        ),
    )
    location_forked_path = LocationFactDefinition(
        key="forked_path",
        text_move_to=(
            "A rough fork in the trail cuts through stony ground where the worn "
            "tracks divide."
        ),
    )
    location_hollow_path = LocationFactDefinition(
        key="hollow_path",
        text_move_to=(
            "A quiet path runs through a shallow hollow where the air is cool and "
            "still."
        ),
    )
    big_chest = ContainerFactDefinition(
        key="chest",
        name="Big chest",
        text_enter="Beside the old tent sits a large chest.",
        text_examine=(
            "The chest is broad and heavy, its lid sitting open as if someone left "
            "in a hurry."
        ),
        text_look="You look inside the chest.",
        text_contents="A big chest sits near the tent.",
    )
    escape_module = EscapeModule(location_beach, location_plane_site)
    cave_module = CaveModule(
        location_ridge,
        character_player.to_pattern(),
        lantern_container=big_chest,
        cave_items_to_reveal=[escape_module.get_item()],
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
    world.add_definition(UseItemFunctionDefinition(character_player.to_pattern()))
    world.add_definition(SynchronizeTickFunctionDefinition())

    world.add_definition(
        TriggerFunctionDefinition(
            MoveEventPattern("$from", "$to"),
            [
                OnMoveUpdateAt(character_player.to_pattern()),
                OnMoveUpdateTick(),
                OnMoveShowEnterText(),
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
            [OnUseFallbackPrint()],
        )
    )
    world.add_definition(
        TriggerFunctionDefinition(
            UseItemEventPattern("$what"),
            [OnUseItemFallbackPrint()],
        )
    )
    world.add_definition(
        TriggerFunctionDefinition(
            StartupEventPattern(),
            [
                OnEventPrint(
                    "You awaken beneath ancient trees, alone in a quiet glade."
                ),
                OnStartupShowEnterText(character_player.to_pattern()),
            ],
        )
    )

    world.add_definition(character_player)

    world.add_definition(location_glade)
    world.add_definition(location_beach)
    world.add_definition(location_camping_site)
    world.add_definition(location_ridge)
    world.add_definition(location_shore_path)
    world.add_definition(location_forest_path)
    world.add_definition(location_plane_site)
    world.add_definition(location_forked_path)
    world.add_definition(location_hollow_path)
    cave_module.apply(world)
    escape_module.apply(world)

    add_route(
        world,
        location_glade,
        Direction.NORTH,
        location_ridge,
        "To the north, the ground rises toward a narrow ridge of pale stone.",
        "To the south, the ridge slopes down toward the shelter of the glade.",
    )
    add_route(
        world,
        location_ridge,
        Direction.NORTH,
        cave_module.cave_location,
        "To the north, a dark opening leads into the cold cave ahead.",
        "To the south, faint daylight spills back across the ridge outside.",
    )
    add_route(
        world,
        location_glade,
        Direction.EAST,
        location_shore_path,
        "To the east, a sandy trail winds toward the distant shore.",
        "To the west, the trail climbs back inland toward the quiet glade.",
    )
    add_route(
        world,
        location_shore_path,
        Direction.EAST,
        location_beach,
        "To the east, the trail descends the last stretch onto the beach.",
        "To the west, a sandy trail leads back inland from the water's edge.",
    )
    add_route(
        world,
        location_glade,
        Direction.SOUTH,
        location_forest_path,
        "To the south, a dim trail slips beneath the trees.",
        "To the north, the trees thin toward the light of the glade.",
    )
    add_route(
        world,
        location_forest_path,
        Direction.EAST,
        location_plane_site,
        "To the east, the trees open around a stretch of torn earth and broken timber.",
        "To the west, a narrow way leads back from the wreck into the forest.",
    )
    add_route(
        world,
        location_forest_path,
        Direction.SOUTH,
        location_forked_path,
        "To the south, the trail continues until the ground opens into a fork.",
        "To the north, the trail narrows beneath the forest canopy.",
    )
    add_route(
        world,
        location_forked_path,
        Direction.WEST,
        location_hollow_path,
        "To the west, a quieter branch turns into a shallow hollow.",
        "To the east, the hollow path rises toward the fork.",
    )
    add_route(
        world,
        location_forked_path,
        Direction.SOUTH,
        location_camping_site,
        "To the south, the trail drops toward an old campsite.",
        "To the north, a worn path leads from the campsite to the fork.",
    )

    world.add_definition(
        StateWrapperDefinition(AtFactPattern(character_player.key, location_glade.key))
    )

    disturbed_soil = ItemFactDefinition(
        key="disturbed_soil",
        name="Disturbed soil",
        text_pickup="",
        text_drop="",
        text_examine=(
            "The earth has been turned recently, leaving the soil loose and uneven "
            "against the surrounding ground."
        ),
        text_enter=(
            "A patch of disturbed soil stands out here. The ground looks recently "
            "turned."
        ),
        text_look="The disturbed soil is loose and shallow.",
        can_pickup=False,
    )
    world.add_definition(disturbed_soil)
    world.add_definition(
        StateWrapperDefinition(
            AtFactPattern(disturbed_soil.key, location_shore_path.key)
        )
    )

    iron_box = ContainerFactDefinition(
        key="iron_box",
        name="Iron box",
        text_pickup="You pick up the iron box.",
        text_drop="You drop the iron box.",
        text_examine=(
            "The iron box is small and heavy in the hand, its rusted seams still "
            "clamped tightly shut."
        ),
        text_enter="Half-buried in the loose soil is a small iron box.",
        text_look="You pry at the rusted lid and look inside the iron box.",
        text_contents="A small iron box lies here, its lid rusted almost shut.",
        can_pickup=True,
    )
    world.add_definition(iron_box)

    container_hollow_tree_trunk = ContainerFactDefinition(
        key="tree_trunk",
        name="Hollow tree trunk",
        text_enter="An old tree trunk stands here, and it looks hollow.",
        text_examine=(
            "The trunk is split and weathered, and the dark hollow inside is just "
            "wide enough to hide something."
        ),
        text_look="You put your hand inside the tree trunk.",
        text_contents="An old hollow tree trunk stands nearby.",
    )
    world.add_definition(container_hollow_tree_trunk)
    world.add_definition(
        StateWrapperDefinition(
            AtFactPattern(container_hollow_tree_trunk.key, location_forest_path.key)
        )
    )

    container_rock_formation = ContainerFactDefinition(
        key="rock_formation",
        name="Suspicious rock formation",
        text_enter=(
            "A strange rock formation rises here. A narrow gap runs between the stones."
        ),
        text_examine=(
            "The stones look too neatly arranged to be natural, and a narrow gap "
            "cuts between them."
        ),
        text_look="You look inside the gap between the rocks.",
        text_contents="A suspicious rock formation has a narrow gap between the rocks.",
    )
    world.add_definition(container_rock_formation)
    world.add_definition(
        StateWrapperDefinition(
            AtFactPattern(container_rock_formation.key, location_forked_path.key)
        )
    )

    world.add_definition(big_chest)
    world.add_definition(
        StateWrapperDefinition(AtFactPattern(big_chest.key, location_camping_site.key))
    )

    shovel = ItemFactDefinition(
        key="shovel",
        name="Shovel",
        text_enter="An old shovel leans here within easy reach.",
        text_examine=(
            "Its wood is worn smooth with age, but the metal blade still looks "
            "strong enough to dig."
        ),
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

    abandoned_well = ContainerFactDefinition(
        key="well",
        name="Abandoned well",
        text_enter="An abandoned well yawns here, ringed with worn stone.",
        text_examine=(
            "The stone lining is cracked and dry, and the bucket hanging within "
            "suggests the water is long gone."
        ),
        text_look="You look inside the well.",
        text_contents="An abandoned well opens in the ground here.",
    )
    world.add_definition(abandoned_well)
    world.add_definition(
        StateWrapperDefinition(
            AtFactPattern(abandoned_well.key, location_hollow_path.key)
        )
    )

    bucket = ContainerFactDefinition(
        key="bucket",
        name="Bucket",
        text_enter="A worn bucket rests here.",
        text_examine=(
            "The bucket is made of old wood bound with iron hoops, its rope handle "
            "frayed with age."
        ),
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
        text_enter="Half-set in the sand is a small seashell.",
        text_examine=(
            "Its pale surface has been polished smooth by the tide, and the shell "
            "stands slightly open."
        ),
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
        text_enter=("A narrow waterfall spills down the rocks here beside the beach."),
        text_examine=(
            "Cold water sheets over the dark rock and disappears into a shallow pool "
            "at the base."
        ),
        text_look="You peer through the falling water.",
        text_contents="A narrow waterfall spills down the rocks beside the beach.",
    )
    world.add_definition(waterfall)
    world.add_definition(
        StateWrapperDefinition(AtFactPattern(waterfall.key, location_beach.key))
    )

    CompassModule(character_player.to_pattern(), location_glade).apply(world)
    CabinModule(
        location_hollow_path,
        seashell,
        [cave_module.lantern_oil],
    ).apply(world)
    StatuesModule(
        character_player.to_pattern(),
        location_ridge,
        [
            iron_box,
            container_hollow_tree_trunk,
            container_rock_formation,
            big_chest,
            bucket,
            waterfall,
        ],
        cave_entrance_block=cave_module.entrance_block,
    ).apply(world)

    world.add_definition(StateWrapperDefinition(TickFactPattern("1")))

    return world


def add_route(
    world: World,
    location_from: LocationFactDefinition,
    direction: Direction,
    locations_to: LocationFactDefinition,
    forward_description: str,
    backward_description: str,
):
    world.add_definition(
        RouteFactDefinition(
            location_from.key,
            direction.value,
            locations_to.key,
            forward_description,
        )
    )
    world.add_definition(
        RouteFactDefinition(
            locations_to.key,
            direction.opposite.value,
            location_from.key,
            backward_description,
        )
    )

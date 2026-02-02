from hyperon import MeTTa
from utils.response import ResponseText, parse_response_atom


def _find_response_atoms(output: str) -> list[str]:
    atoms = []
    index = 0
    length = len(output)
    in_string = False
    escape = False

    while index < length:
        char = output[index]
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            index += 1
            continue

        if char == '"':
            in_string = True
            index += 1
            continue

        if output.startswith("(Response", index):
            atom, next_index = _extract_sexpr(output, index)
            if atom:
                atoms.append(atom)
                index = next_index
                continue

        index += 1

    return atoms


def _extract_sexpr(text: str, start_index: int) -> tuple[str | None, int]:
    depth = 0
    index = start_index
    length = len(text)
    in_string = False
    escape = False

    while index < length:
        char = text[index]
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            index += 1
            continue

        if char == '"':
            in_string = True
            index += 1
            continue

        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return text[start_index : index + 1], index + 1

        index += 1

    return None, start_index


def _parse_response_atom(atom: str) -> ResponseText | None:
    return parse_response_atom(atom)


def _format_metta_output(output: str) -> str:
    if isinstance(output, str):
        atoms = _find_response_atoms(output)
        if not atoms:
            return output
        responses: list[ResponseText] = []
        for atom in atoms:
            response = _parse_response_atom(atom)
            if response and response.text:
                responses.append(response)
        responses.sort(key=lambda item: (-item.priority, item.text))
        return "\n".join(item.text for item in responses)

    responses: list[ResponseText] = []
    for atom in _iter_metta_atoms(output):
        response = _parse_response_atom(atom)
        if response and response.text:
            responses.append(response)
    if not responses:
        return str(output)
    responses.sort(key=lambda item: (-item.priority, item.text))
    return "\n".join(item.text for item in responses)


def _iter_metta_atoms(output):
    if isinstance(output, list):
        for row in output:
            if isinstance(row, list):
                for atom in row:
                    yield atom
            else:
                yield row
        return
    yield output

from core.definitions.facts.character_fact_definition import CharacterFactDefinition
from core.definitions.facts.location_fact_definition import LocationFactDefinition
from core.definitions.facts.route_fact_definition import RouteFactDefinition
from core.definitions.wrappers.state_wrapper_definition import StateWrapperDefinition
from core.patterns.events.drop_event_pattern import DropEventPattern
from core.patterns.events.pickup_event_pattern import PickUpEventPattern
from core.patterns.events.use_event_pattern import UseEventPattern
from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.patterns.facts.tick_fact_pattern import TickFactPattern
from core.patterns.functions.synchronize_tick_function_pattern import (
    SynchronizeTickFunctionPattern,
)
from core.patterns.functions.trigger_function_pattern import TriggerFunctionPattern
from core.world import World
from core.patterns.events.move_event_pattern import MoveEventPattern
from core.definitions.functions.exists_function_definition import (
    ExistsFunctionDefinition,
)
from core.definitions.functions.first_function_definition import (
    FirstFunctionDefinition,
)
from core.definitions.functions.last_function_definition import LastFunctionDefinition
from core.definitions.functions.inventory_function_definition import (
    InventoryFunctionPattern as InventoryFunctionDefinition,
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
from core.definitions.functions.drop_function_definition import DropFunctionDefinition
from core.definitions.functions.synchronize_tick_function_definition import (
    SynchronizeTickFunctionDefinition,
)
from core.definitions.functions.use_function_definition import UseFunctionDefinition
from core.definitions.functions.trigger_function_definition import (
    TriggerFunctionDefinition,
)
from core.definitions.side_effects.on_drop_update_at import OnDropUpdateAt
from core.definitions.side_effects.on_event_print import OnEventPrint
from core.definitions.side_effects.on_move_show_items import OnMoveShowItems
from core.definitions.side_effects.on_move_update_at import OnMoveUpdateAt
from core.definitions.side_effects.on_move_update_tick import OnMoveUpdateTick
from core.definitions.side_effects.on_pickup_update_at import OnPickUpUpdateAt
from core.definitions.side_effects.on_startup_show_items import OnStartupShowItems
from core.definitions.side_effects.on_use_do_nothing import OnUseDoNothing
from modules.compass.compass_module import CompassModule
from modules.cave_entrance.cave_entrance_module import CaveEntranceModule
from utils.direction import Direction
from core.patterns.events.startup_event_pattern import StartupEventPattern
from core.nlp import EmbeddingIndex, build_command_catalog


def main():
    metta = MeTTa()
    world = build_world()
    metta_code = world.to_metta()
    command_catalog = build_command_catalog(world)
    embedding_index = EmbeddingIndex(
        command_catalog, model_name="BAAI/bge-small-en-v1.5"
    )

    print(metta_code)
    print(metta.run(metta_code))
    startup_output = metta.run(
        f"!{TriggerFunctionPattern(StartupEventPattern()).to_metta()}"
    )
    print(_format_metta_output(startup_output))
    print(f"\n--- Command Catalog ({len(command_catalog)}) ---")
    for entry in command_catalog:
        print(f"{entry.utterance} -> {entry.metta}")

    print("\n--- MeTTa Console ---")
    print("Type 'exit' to quit.")

    while True:
        user_query = input(">> ")

        if user_query.strip().lower() in ("exit", "quit"):
            break

        stripped = user_query.strip()
        if stripped.startswith("!") or stripped.startswith("("):
            metta_query = stripped
        else:
            match = embedding_index.match(stripped)
            if match is None:
                print("No commands available.")
                continue
            print(f"[NL] {stripped} -> {match.entry.metta} ({match.score:.3f})")
            metta_query = f"!{match.entry.metta}"

        result_output = metta.run(metta_query)
        print(_format_metta_output(result_output))
        print(metta.run(f"!{SynchronizeTickFunctionPattern().to_metta()}"))


def build_world():
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
    world.add_definition(LocationPathFunctionDefinition())
    world.add_definition(InventoryFunctionDefinition(character_player.to_pattern()))
    world.add_definition(MoveToFunctionDefinition(character_player.to_pattern()))
    world.add_definition(MoveTowardsFunctionDefinition(character_player.to_pattern()))
    world.add_definition(PickUpFunctionDefinition(character_player.to_pattern()))
    world.add_definition(DropFunctionDefinition(character_player.to_pattern()))
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


if __name__ == "__main__":
    main()

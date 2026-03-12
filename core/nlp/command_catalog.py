from dataclasses import dataclass
from itertools import product

from core.nlp.nl_spec import NLSpec
from utils.direction import Direction


@dataclass(frozen=True)
class SlotValue:
    key: str
    text: str


@dataclass(frozen=True)
class CommandEntry:
    utterance: str
    intent: str
    metta: str
    slots: dict[str, str]


def _humanize_key(value: str) -> str:
    return value.replace("_", " ")


def _unwrap_atom(atom) -> str:
    if hasattr(atom, "get_object"):
        obj = atom.get_object()
        if hasattr(obj, "value"):
            return str(obj.value)
        if hasattr(obj, "content"):
            return str(obj.content)
        return str(obj)
    if hasattr(atom, "get_name"):
        return atom.get_name()
    return str(atom)


def _query_values(metta, pattern: str, value: str) -> list[str]:
    result = metta.run(f"!(match &self {pattern} {value})")
    values: list[str] = []
    for match in result:
        for atom in match:
            values.append(_unwrap_atom(atom))
    return values


def _active_keys(metta) -> set[str]:
    return set(_query_values(metta, "(State (At $what $where))", "$what"))


def _resolve_active_entities(metta, fact_name: str) -> list[SlotValue]:
    active_keys = _active_keys(metta)
    typed_keys = set(_query_values(metta, f"({fact_name} $key)", "$key"))
    keys = sorted(active_keys & typed_keys)
    return [SlotValue(key=key, text=_humanize_key(key).lower()) for key in keys]


def _resolve_items(metta, _world) -> list[SlotValue]:
    return _resolve_active_entities(metta, "Item")


def _resolve_examinables(metta, _world) -> list[SlotValue]:
    items = _resolve_items(metta, _world)
    containers = _resolve_containers(metta, _world)
    seen: set[tuple[str, str]] = set()
    values: list[SlotValue] = []
    for value in items + containers:
        key = (value.key, value.text)
        if key in seen:
            continue
        seen.add(key)
        values.append(value)
    return values


def _resolve_locations(metta, _world) -> list[SlotValue]:
    keys = sorted(set(_query_values(metta, "(Location $key)", "$key")))
    return [SlotValue(key=k, text=_humanize_key(k)) for k in keys]


def _resolve_containers(metta, _world) -> list[SlotValue]:
    return _resolve_active_entities(metta, "Container")


def _resolve_directions(_metta, _world) -> list[SlotValue]:
    keys = [direction.value for direction in Direction]
    return [SlotValue(key=k, text=k) for k in keys]


DEFAULT_SLOT_RESOLVERS = {
    "item": _resolve_items,
    "examinable": _resolve_examinables,
    "location": _resolve_locations,
    "container": _resolve_containers,
    "direction": _resolve_directions,
}


def build_command_catalog(world, metta, slot_resolvers=None) -> list[CommandEntry]:
    resolver_map = dict(DEFAULT_SLOT_RESOLVERS)
    if slot_resolvers:
        resolver_map.update(slot_resolvers)

    entries: list[CommandEntry] = []
    seen: set[tuple[str, str]] = set()

    for definition in world.definitions:
        spec: NLSpec | None = definition.nl_spec()
        if not spec:
            continue

        slot_specs = list(spec.slots.items())
        if not slot_specs:
            for template in spec.templates:
                key = (template, spec.metta)
                if key in seen:
                    continue
                seen.add(key)
                entries.append(
                    CommandEntry(
                        utterance=template,
                        intent=spec.intent,
                        metta=spec.metta,
                        slots={},
                    )
                )
            continue

        slot_values: list[tuple[str, list[SlotValue]]] = []
        for slot_name, slot_spec in slot_specs:
            resolver = resolver_map.get(slot_spec.slot_type)
            if resolver is None:
                raise ValueError(f"Missing slot resolver for '{slot_spec.slot_type}'")
            slot_values.append((slot_name, resolver(metta, world)))

        slot_names = [name for name, _ in slot_values]
        value_lists = [values for _, values in slot_values]

        for value_combo in product(*value_lists):
            slot_value_map = {
                name: value.key for name, value in zip(slot_names, value_combo)
            }
            slot_text_map = {
                name: value.text for name, value in zip(slot_names, value_combo)
            }
            for template in spec.templates:
                utterance = template.format(**slot_text_map)
                metta_command = spec.metta.format(**slot_value_map)
                key = (utterance, metta_command)
                if key in seen:
                    continue
                seen.add(key)
                entries.append(
                    CommandEntry(
                        utterance=utterance,
                        intent=spec.intent,
                        metta=metta_command,
                        slots=slot_value_map,
                    )
                )

    return entries

from dataclasses import dataclass
from itertools import product

from core.definitions.facts.container_fact_definition import ContainerFactDefinition
from core.definitions.facts.item_fact_definition import ItemFactDefinition
from core.definitions.facts.location_fact_definition import LocationFactDefinition
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


def _resolve_items(world) -> list[SlotValue]:
    keys = sorted(
        {d.key for d in world.definitions if isinstance(d, ItemFactDefinition)}
    )
    return [SlotValue(key=k, text=_humanize_key(k)) for k in keys]


def _resolve_locations(world) -> list[SlotValue]:
    keys = sorted(
        {d.key for d in world.definitions if isinstance(d, LocationFactDefinition)}
    )
    return [SlotValue(key=k, text=_humanize_key(k)) for k in keys]


def _resolve_containers(world) -> list[SlotValue]:
    keys = sorted(
        {d.key for d in world.definitions if isinstance(d, ContainerFactDefinition)}
    )
    return [SlotValue(key=k, text=_humanize_key(k)) for k in keys]


def _resolve_directions(_world) -> list[SlotValue]:
    keys = [direction.value for direction in Direction]
    return [SlotValue(key=k, text=k) for k in keys]


DEFAULT_SLOT_RESOLVERS = {
    "item": _resolve_items,
    "location": _resolve_locations,
    "container": _resolve_containers,
    "direction": _resolve_directions,
}


def build_command_catalog(world, slot_resolvers=None) -> list[CommandEntry]:
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
            slot_values.append((slot_name, resolver(world)))

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
                metta = spec.metta.format(**slot_value_map)
                key = (utterance, metta)
                if key in seen:
                    continue
                seen.add(key)
                entries.append(
                    CommandEntry(
                        utterance=utterance,
                        intent=spec.intent,
                        metta=metta,
                        slots=slot_value_map,
                    )
                )

    return entries

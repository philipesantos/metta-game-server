from core.definitions.fact_definition import FactDefinition
from core.definitions.functions.trigger_function_definition import (
    TriggerFunctionDefinition,
)
from core.definitions.side_effects.on_event_print import OnEventPrint
from core.patterns.events.drop_event_pattern import DropEventPattern
from core.patterns.events.examine_event_pattern import ExamineEventPattern
from core.patterns.events.pickup_event_pattern import PickUpEventPattern
from core.patterns.facts.item_fact_pattern import ItemFactPattern
from core.patterns.facts.pickupable_fact_pattern import PickupableFactPattern
from utils.type import Type


class ItemFactDefinition(FactDefinition):
    NAME_FACT = "ItemName"
    ENTER_TEXT_FACT = "ItemEnterText"
    LOOK_TEXT_FACT = "ItemLookText"
    ENTER_PRIORITY_FACT = "ItemEnterPriority"
    LOOK_PRIORITY_FACT = "ItemLookPriority"

    def __init__(
        self,
        key: str,
        text_pickup: str,
        text_drop: str,
        text_examine: str,
        name: str | None = None,
        text_enter: str | None = None,
        text_look: str | None = None,
        enter_priority: int = 20,
        look_priority: int = 20,
        can_pickup: bool = True,
    ):
        self.key = key
        self.text_pickup = text_pickup
        self.text_drop = text_drop
        self.text_examine = text_examine
        self.name = name or self._default_name(key)
        self.text_enter = text_enter
        self.text_look = text_look or self._default_descriptive_text(key)
        self.enter_priority = enter_priority
        self.look_priority = look_priority
        self.can_pickup = can_pickup

    def to_metta(self) -> str:
        trigger_pickup = TriggerFunctionDefinition(
            PickUpEventPattern(self.key, "$where"), [OnEventPrint(self.text_pickup)]
        )
        trigger_drop = TriggerFunctionDefinition(
            DropEventPattern(self.key, "$where"), [OnEventPrint(self.text_drop)]
        )
        trigger_examine = TriggerFunctionDefinition(
            ExamineEventPattern(self.key), [OnEventPrint(self.text_examine)]
        )
        pickupable = (
            f"{PickupableFactPattern(self.key).to_metta()}\n" if self.can_pickup else ""
        )
        item_name = f'({self.NAME_FACT} {self.key} {self._quote(self.name)})\n'
        item_enter_text = (
            f'({self.ENTER_TEXT_FACT} {self.key} {self._quote(self.text_enter)})\n'
            if self.text_enter is not None
            else ""
        )
        item_look_text = (
            f'({self.LOOK_TEXT_FACT} {self.key} {self._quote(self.text_look)})\n'
        )
        item_enter_priority = (
            f"({self.ENTER_PRIORITY_FACT} {self.key} {self.enter_priority})\n"
            if self.text_enter is not None
            else ""
        )
        item_look_priority = (
            f"({self.LOOK_PRIORITY_FACT} {self.key} {self.look_priority})\n"
        )
        # fmt: off
        return (
            f"(: {self.key} {Type.ITEM.value})\n"
            f"{ItemFactPattern(self.key).to_metta()}\n"
            f"{item_name}"
            f"{item_enter_text}"
            f"{item_look_text}"
            f"{item_enter_priority}"
            f"{item_look_priority}"
            f"{pickupable}"
            f"{trigger_pickup.to_metta()}\n"
            f"{trigger_drop.to_metta()}\n"
            f"{trigger_examine.to_metta()}"
        )
        # fmt: on

    @staticmethod
    def _default_descriptive_text(key: str) -> str:
        return f"You notice {ItemFactDefinition._default_name(key)}."

    @staticmethod
    def _default_name(key: str) -> str:
        return key.replace("_", " ")

    @staticmethod
    def _quote(text: str) -> str:
        escaped = text.replace('\\', '\\\\').replace('"', '\\"')
        return f'"{escaped}"'

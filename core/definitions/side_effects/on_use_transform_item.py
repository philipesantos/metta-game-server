from core.definitions.facts.item_fact_definition import ItemFactDefinition
from core.definitions.side_effect_definition import SideEffectDefinition
from core.patterns.events.use_event_pattern import UseEventPattern
from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.patterns.wrappers.state_wrapper_pattern import StateWrapperPattern
from core.utils.metta_expressions import split_expressions


class OnUseTransformItem(SideEffectDefinition):
    def __init__(
        self,
        from_item: ItemFactDefinition,
        to_item: ItemFactDefinition,
        consumed_item_key: str,
    ):
        self.from_item = from_item
        self.to_item = to_item
        self.consumed_item_key = consumed_item_key

    def to_metta(self, event: UseEventPattern) -> str:
        from_item_state = StateWrapperPattern(
            AtFactPattern(self.from_item.key, "$from_item_where")
        )
        to_item_state = StateWrapperPattern(AtFactPattern(self.to_item.key, "$from_item_where"))
        consumed_item_state = StateWrapperPattern(
            AtFactPattern(self.consumed_item_key, "$consumed_item_where")
        )
        remove_from_definition = "\n".join(
            f"    (() (remove-atom &self {expression}))"
            for expression in split_expressions(self.from_item.to_metta())
        )
        remove_to_definition = "\n".join(
            f"    (() (remove-atom &self {expression}))"
            for expression in split_expressions(self.to_item.to_metta())
        )
        add_to_definition = "\n".join(
            f"    (() (add-atom &self {expression}))"
            for expression in split_expressions(self.to_item.to_metta())
        )
        return (
            f"(let* (\n"
            f"{remove_from_definition}\n"
            f"{remove_to_definition}\n"
            f"{add_to_definition}\n"
            f"    (() (match &self {from_item_state.to_metta()} (remove-atom &self {from_item_state.to_metta()})))\n"
            f"    (() (add-atom &self {to_item_state.to_metta()}))\n"
            f"    (() (match &self {consumed_item_state.to_metta()} (remove-atom &self {consumed_item_state.to_metta()})))\n"
            f")\n"
            f"    Empty\n"
            f")\n"
        )

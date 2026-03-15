from core.definitions.function_definition import FunctionDefinition
from core.nlp.nl_spec import NLSpec, SlotSpec
from core.patterns.events.examine_event_pattern import ExamineEventPattern
from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.patterns.facts.character_fact_pattern import CharacterFactPattern
from core.patterns.facts.response_fact_pattern import ResponseFactPattern
from core.patterns.functions.exists_function_pattern import ExistsFunctionPattern
from core.patterns.functions.trigger_function_pattern import TriggerFunctionPattern
from core.patterns.wrappers.state_wrapper_pattern import StateWrapperPattern


class ExamineFunctionDefinition(FunctionDefinition):
    def __init__(self, character: CharacterFactPattern):
        self.character = character

    def to_metta(self) -> str:
        state_at_player = StateWrapperPattern(
            AtFactPattern(self.character.key, "$where")
        )
        state_at_item_here = StateWrapperPattern(AtFactPattern("$what", "$where"))
        state_at_item_inventory = StateWrapperPattern(
            AtFactPattern("$what", self.character.key)
        )
        item_here_exists = ExistsFunctionPattern(state_at_item_here)
        item_inventory_exists = ExistsFunctionPattern(state_at_item_inventory)
        examine_event = ExamineEventPattern("$what")
        examine_trigger = TriggerFunctionPattern(examine_event)
        # fmt: off
        return (
            f"(= (examine ($what))\n"
            f"    (let $where (match &self {state_at_player.to_metta()} $where)\n"
            f"        (if (or {item_here_exists.to_metta()} {item_inventory_exists.to_metta()})\n"
            f"            {examine_trigger.to_metta()}\n"
            f"            {ResponseFactPattern(100, '\"You do not see anything like that here.\"').to_metta()}\n"
            f"        )\n"
            f"    )\n"
            f")"
        )
        # fmt: on

    def nl_spec(self):
        return NLSpec(
            intent="examine",
            templates=(
                "examine {target}",
                "inspect {target}",
                "look at {target}",
                "check {target}",
            ),
            metta="(examine ({target}))",
            slots={"target": SlotSpec("examinable")},
        )

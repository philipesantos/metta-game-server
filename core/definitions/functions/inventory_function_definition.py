from core.definitions.function_definition import FunctionDefinition
from core.patterns.facts.character_fact_pattern import CharacterFactPattern
from core.patterns.facts.response_fact_pattern import ResponseFactPattern
from core.nlp.nl_spec import NLSpec


class InventoryFunctionPattern(FunctionDefinition):
    def __init__(self, character: CharacterFactPattern):
        self.character = character

    def to_metta(self) -> str:
        # fmt: off
        return (
            f"(= (inventory)\n"
            f"    (let $result (collapse (match &self (State (At $what {self.character.key}))\n"
            f"        (let $item_result (match &self (ItemName $what $name) {ResponseFactPattern(20, '$name').to_metta()})\n"
            f"            (case $item_result (\n"
            f"                (() (let $container_result (match &self (ContainerName $what $name) {ResponseFactPattern(20, '$name').to_metta()})\n"
            f"                    (case $container_result (\n"
            f"                        (() {ResponseFactPattern(20, '(Text \"You have \" $what \".\")').to_metta()})\n"
            f"                        ($_ $container_result)\n"
            f"                    ))\n"
            f"                ))\n"
            f"                ($_ $item_result)\n"
            f"            ))\n"
            f"        )\n"
            f"    ))\n"
            f"        (case $result (\n"
            f'            (() {ResponseFactPattern(20, "\"Your inventory is empty.\"").to_metta()})\n'
            f"            ($_ $result)\n"
            f"        ))\n"
            f"    )\n"
            f")"
        )
        # fmt: on

    def nl_spec(self):
        return NLSpec(
            intent="inventory",
            templates=("inventory", "show inventory", "what do i have"),
            metta="(inventory)",
            slots={},
        )

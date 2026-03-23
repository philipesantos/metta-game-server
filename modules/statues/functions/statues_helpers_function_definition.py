from core.definitions.function_definition import FunctionDefinition
from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.patterns.facts.response_fact_pattern import ResponseFactPattern
from core.patterns.functions.exists_function_pattern import ExistsFunctionPattern
from core.patterns.wrappers.state_wrapper_pattern import StateWrapperPattern


class StatuesHelpersFunctionDefinition(FunctionDefinition):
    def to_metta(self) -> str:
        return "\n\n".join(
            (
                self._statue_has_any_rune(),
                self._all_statues_filled(),
                self._statues_solved(),
                self._statue_filled_message(),
            )
        )

    def _statue_has_any_rune(self) -> str:
        return (
            "(= (statue-has-any-rune ($statue))\n"
            f"{self._indent_block(self._or_chain(self._statue_rune_exists('$statue')))}\n"
            ")"
        )

    def _all_statues_filled(self) -> str:
        return (
            "(= (all-statues-filled)\n"
            f"{self._indent_block(self._and_chain([self._statue_has_any_rune_call(statue_key) for statue_key in self._statue_keys()]))}\n"
            ")"
        )

    def _statues_solved(self) -> str:
        return (
            "(= (statues-solved)\n"
            f"{self._indent_block(self._and_chain([self._state_exists(rune_key, statue_key) for rune_key, statue_key in self._solution_mapping()]))}\n"
            ")"
        )

    def _statue_filled_message(self) -> str:
        return (
            "(= (statue-filled-message ($statue $statue_name))\n"
            f"{self._indent_block(self._filled_message_body('$statue', '$statue_name'))}\n"
            ")"
        )

    def _filled_message_body(self, statue_key: str, statue_name: str) -> str:
        rune_names = {
            "epsilon_rune": "epsilon rune",
            "gamma_rune": "gamma rune",
            "omicron_rune": "omicron rune",
        }
        current = ""
        for rune_key in reversed(self._rune_keys()):
            rune_message = ResponseFactPattern(
                100,
                f'(Text "The " {statue_name} " already holds the {rune_names[rune_key]}.")',
            ).to_metta()
            if not current:
                current = rune_message
                continue
            current = self._format_if(
                self._state_exists(rune_key, statue_key),
                rune_message,
                current,
            )
        return current

    def _statue_rune_exists(self, statue_key: str) -> list[str]:
        return [self._state_exists(rune_key, statue_key) for rune_key in self._rune_keys()]

    @staticmethod
    def _solution_mapping() -> tuple[tuple[str, str], ...]:
        return (
            ("epsilon_rune", "lion_statue"),
            ("gamma_rune", "eagle_statue"),
            ("omicron_rune", "bear_statue"),
        )

    @staticmethod
    def _rune_keys() -> tuple[str, ...]:
        return ("epsilon_rune", "gamma_rune", "omicron_rune")

    @staticmethod
    def _statue_keys() -> tuple[str, ...]:
        return ("lion_statue", "eagle_statue", "bear_statue")

    @staticmethod
    def _state_exists(rune_key: str, statue_key: str) -> str:
        return ExistsFunctionPattern(
            StateWrapperPattern(AtFactPattern(rune_key, statue_key))
        ).to_metta()

    @staticmethod
    def _statue_has_any_rune_call(statue_key: str) -> str:
        return f"(statue-has-any-rune ({statue_key}))"

    @staticmethod
    def _indent_block(text: str, indent: str = "    ") -> str:
        return "\n".join(
            f"{indent}{line}" if line else line for line in text.splitlines()
        )

    @classmethod
    def _format_binary(cls, operator: str, left: str, right: str) -> str:
        return (
            f"({operator}\n"
            f"{cls._indent_block(left)}\n"
            f"{cls._indent_block(right)}\n"
            ")"
        )

    @classmethod
    def _format_if(cls, condition: str, when_true: str, when_false: str) -> str:
        return (
            "(if\n"
            f"{cls._indent_block(condition)}\n"
            f"{cls._indent_block(when_true)}\n"
            f"{cls._indent_block(when_false)}\n"
            ")"
        )

    @classmethod
    def _or_chain(cls, conditions: list[str]) -> str:
        if len(conditions) == 1:
            return conditions[0]
        current = cls._format_binary("or", conditions[0], conditions[1])
        for condition in conditions[2:]:
            current = cls._format_binary("or", current, condition)
        return current

    @classmethod
    def _and_chain(cls, conditions: list[str]) -> str:
        if len(conditions) == 1:
            return conditions[0]
        current = cls._format_binary("and", conditions[0], conditions[1])
        for condition in conditions[2:]:
            current = cls._format_binary("and", current, condition)
        return current

from core.definitions.side_effect_definition import SideEffectDefinition
from core.patterns.events.use_event_pattern import UseEventPattern
from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.patterns.facts.character_fact_pattern import CharacterFactPattern
from core.patterns.facts.response_fact_pattern import ResponseFactPattern
from core.patterns.wrappers.state_wrapper_pattern import StateWrapperPattern
from modules.cave.cave_entrance_block import CaveEntranceBlock


class StatuesModuleOnUseRuneOnStatue(SideEffectDefinition):
    def __init__(
        self,
        character: CharacterFactPattern,
        rune_key: str,
        rune_name: str,
        statue_key: str,
        statue_name: str,
        cave_entrance_block: CaveEntranceBlock | None = None,
    ):
        self.character = character
        self.rune_key = rune_key
        self.rune_name = rune_name
        self.statue_key = statue_key
        self.statue_name = statue_name
        self.cave_entrance_block = cave_entrance_block

    def to_metta(self, event: UseEventPattern) -> str:
        inventory_state = StateWrapperPattern(
            AtFactPattern(self.rune_key, self.character.key)
        )
        statue_state = StateWrapperPattern(AtFactPattern(self.rune_key, self.statue_key))
        place_message = ResponseFactPattern(
            120,
            self._quote(f"You place the {self.rune_name} into the {self.statue_name}."),
        )
        wrong_message = ResponseFactPattern(
            120,
            self._quote(
                f"You place the {self.rune_name} into the {self.statue_name}. Nothing happens."
            ),
        )
        success_message = ResponseFactPattern(
            200,
            self._quote(
                f"You place the {self.rune_name} into the {self.statue_name}. The runes flare to life, spelling EGO across the statues. In the distance, the great boulder at the cave entrance grinds aside."
            ),
        )
        filled_message = self._filled_message_call()
        slot_filled_condition = self._statue_has_any_rune_call(self.statue_key)
        all_filled_condition = "(all-statues-filled)"
        solved_condition = "(statues-solved)"
        placement_updates = [
            f"(() (remove-atom &self {inventory_state.to_metta()}))",
            f"(() (add-atom &self {statue_state.to_metta()}))",
        ]
        solved_branch = self._format_let_star(
            self._unblock_updates(),
            success_message.to_metta(),
        )
        unsolved_branch = self._format_if(
            all_filled_condition,
            wrong_message.to_metta(),
            place_message.to_metta(),
        )
        body = self._format_if(
            slot_filled_condition,
            filled_message,
            self._format_let_star(
                placement_updates,
                self._format_if(
                    solved_condition,
                    solved_branch,
                    unsolved_branch,
                ),
            ),
        )
        return f"{body}\n"

    def _unblock_updates(self) -> list[str]:
        if self.cave_entrance_block is None:
            return ["(() Empty)"]
        return self.cave_entrance_block.removal_updates(indent="").splitlines()

    @staticmethod
    def _quote(text: str) -> str:
        escaped = text.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'

    def _filled_message_call(self) -> str:
        return (
            f"(statue-filled-message ({self.statue_key} {self._quote(self.statue_name)}))"
        )

    @staticmethod
    def _statue_has_any_rune_call(statue_key: str) -> str:
        return f"(statue-has-any-rune ({statue_key}))"

    @staticmethod
    def _indent_block(text: str, indent: str = "    ") -> str:
        return "\n".join(
            f"{indent}{line}" if line else line for line in text.splitlines()
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
    def _format_let_star(cls, bindings: list[str], body: str) -> str:
        formatted_bindings = "\n".join(
            cls._indent_block(binding) for binding in bindings
        )
        return (
            "(let* (\n"
            f"{formatted_bindings}\n"
            ")\n"
            f"{cls._indent_block(body)}\n"
            ")"
        )

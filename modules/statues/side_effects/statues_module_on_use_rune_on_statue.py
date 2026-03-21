from core.definitions.side_effect_definition import SideEffectDefinition
from core.patterns.events.use_event_pattern import UseEventPattern
from core.patterns.facts.at_fact_pattern import AtFactPattern
from core.patterns.facts.character_fact_pattern import CharacterFactPattern
from core.patterns.facts.response_fact_pattern import ResponseFactPattern
from core.patterns.functions.exists_function_pattern import ExistsFunctionPattern
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
        self.rune_keys = ("epsilon_rune", "gamma_rune", "omicron_rune")
        self.statue_keys = ("lion_statue", "eagle_statue", "bear_statue")
        self.cave_entrance_block = cave_entrance_block

    def to_metta(self, event: UseEventPattern) -> str:
        inventory_state = StateWrapperPattern(
            AtFactPattern(self.rune_key, self.character.key)
        )
        statue_state = StateWrapperPattern(AtFactPattern(self.rune_key, self.statue_key))
        filled_states = [
            StateWrapperPattern(AtFactPattern(rune_key, self.statue_key))
            for rune_key in self.rune_keys
        ]
        lion_filled = self._filled_condition("lion_statue")
        eagle_filled = self._filled_condition("eagle_statue")
        bear_filled = self._filled_condition("bear_statue")
        solved_state = (
            ExistsFunctionPattern(
                StateWrapperPattern(AtFactPattern("epsilon_rune", "lion_statue"))
            ).to_metta(),
            ExistsFunctionPattern(
                StateWrapperPattern(AtFactPattern("gamma_rune", "eagle_statue"))
            ).to_metta(),
            ExistsFunctionPattern(
                StateWrapperPattern(AtFactPattern("omicron_rune", "bear_statue"))
            ).to_metta(),
        )
        place_message = ResponseFactPattern(
            120,
            self._quote(f"You place the {self.rune_name} into the {self.statue_name}."),
        )
        filled_message = ResponseFactPattern(
            100,
            self._quote(f"The slot in the {self.statue_name} is already filled."),
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
        filled_message = self._filled_message()
        slot_filled_condition = self._or_chain(
            [ExistsFunctionPattern(state).to_metta() for state in filled_states]
        )
        all_filled_condition = self._and_chain([lion_filled, eagle_filled, bear_filled])
        solved_condition = self._and_chain(list(solved_state))
        unblock_updates = self._unblock_updates()
        # fmt: off
        return (
            f"(if {slot_filled_condition}\n"
            f"    {filled_message}\n"
            f"    (let* ((() (remove-atom &self {inventory_state.to_metta()}))\n"
            f"           (() (add-atom &self {statue_state.to_metta()})))\n"
            f"        (if {solved_condition}\n"
            f"            (let* (\n"
            f"{unblock_updates}"
            f"                )\n"
            f"                {success_message.to_metta()}\n"
            f"            )\n"
            f"            (if {all_filled_condition}\n"
            f"                {wrong_message.to_metta()}\n"
            f"                {place_message.to_metta()}\n"
            f"            )\n"
            f"        )\n"
            f"    )\n"
            f")\n"
        )
        # fmt: on

    def _filled_condition(self, statue_key: str) -> str:
        states = [
            StateWrapperPattern(AtFactPattern(rune_key, statue_key))
            for rune_key in self.rune_keys
        ]
        return self._or_chain(
            [ExistsFunctionPattern(state).to_metta() for state in states]
        )

    def _filled_message(self) -> str:
        rune_names = {
            "epsilon_rune": "epsilon rune",
            "gamma_rune": "gamma rune",
            "omicron_rune": "omicron rune",
        }
        current = ""
        for rune_key in reversed(self.rune_keys):
            rune_state = StateWrapperPattern(AtFactPattern(rune_key, self.statue_key))
            rune_message = ResponseFactPattern(
                100,
                self._quote(
                    f"The {self.statue_name} already holds the {rune_names[rune_key]}."
                ),
            ).to_metta()
            if not current:
                current = rune_message
                continue
            current = (
                f"(if {ExistsFunctionPattern(rune_state).to_metta()}\n"
                f"    {rune_message}\n"
                f"    {current}\n"
                f")"
            )
        return current

    def _unblock_updates(self) -> str:
        if self.cave_entrance_block is None:
            return "                (() Empty)\n"
        return self.cave_entrance_block.removal_updates()

    @staticmethod
    def _or_chain(conditions: list[str]) -> str:
        if len(conditions) == 1:
            return conditions[0]
        current = f"(or {conditions[0]} {conditions[1]})"
        for condition in conditions[2:]:
            current = f"(or {current} {condition})"
        return current

    @staticmethod
    def _and_chain(conditions: list[str]) -> str:
        if len(conditions) == 1:
            return conditions[0]
        current = f"(and {conditions[0]} {conditions[1]})"
        for condition in conditions[2:]:
            current = f"(and {current} {condition})"
        return current

    @staticmethod
    def _quote(text: str) -> str:
        escaped = text.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'

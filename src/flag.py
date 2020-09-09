"""Represents a flag of BattleLine."""

import itertools
from typing import Iterable, List, Optional, Sequence, Union

from src.cards.cards import (
    TacticEnvironmentCard,
    TacticMoraleCard,
    TroopAndTacticMoraleCard,
    TroopCard,
)
from src.cards.cardtypes import (
    TacticEnvironments,
    TacticMorales,
    Tactics,
    TroopColors,
    Troops,
)
from src.consts import PLAYER_A, PLAYER_B, PLAYER_UNRESOLVED

_FLAG_REPRESENTATION_FORMAT = """
 {9:^7} 
 {8:^7} 
--- {12:1} ---
 {7:^7} 
 {6:^7} 
 {5:^7} 
--- {10:1} ---
 {0:^7} 
 {1:^7} 
 {2:^7} 
--- {11:1} ---
 {3:^7} 
 {4:^7} 
"""


class Flag:
    @staticmethod
    def repr_flags(flags: Iterable["Flag"]) -> str:
        lines: List[str] = []
        for flag in flags:
            flag_lines = repr(flag).split("\n")
            for i, line in enumerate(flag_lines):
                if len(lines) <= i:
                    lines.append(line)
                else:
                    lines[i] += line
        return "\n".join(lines)

    def __init__(self) -> None:
        self.stacks: List[List[TroopAndTacticMoraleCard]] = [[], []]
        self.envs: List[List[TacticEnvironmentCard]] = [[], []]
        self._last_stacked_player = PLAYER_UNRESOLVED
        self._flag_position = PLAYER_UNRESOLVED

    def is_resolved(self) -> bool:
        return self._flag_position != PLAYER_UNRESOLVED

    def get_resolved(self) -> int:
        return self._flag_position

    def resolve(self, player: int) -> None:
        assert self._flag_position == PLAYER_UNRESOLVED, "the flag is already resolved!"
        self._flag_position = player

    def get_required_card_num(self) -> int:
        stacked_envs = [
            e.get_tactic_envs() for e in itertools.chain.from_iterable(self.envs)
        ]
        return 4 if TacticEnvironments.MUD in stacked_envs else 3

    def is_formation_disabled(self) -> bool:
        stacked_envs = [
            e.get_tactic_envs() for e in itertools.chain.from_iterable(self.envs)
        ]
        return TacticEnvironments.FOG in stacked_envs

    def get_stacked_cards(self, player: int) -> Sequence[TroopAndTacticMoraleCard]:
        return self.stacks[player]

    def get_opposite_stacked_cards(
        self, player: int
    ) -> Sequence[TroopAndTacticMoraleCard]:
        return self.get_stacked_cards(PLAYER_A if player == PLAYER_B else PLAYER_B)

    def get_last_stacked_player(self) -> int:
        return self._last_stacked_player

    def add_stack(self, player: int, card: TroopAndTacticMoraleCard) -> None:
        self.stacks[player].append(card)
        self.stacks[player].sort()
        self._last_stacked_player = player

    def remove_stack(
        self, player: int, card: TroopAndTacticMoraleCard
    ) -> Optional[TroopAndTacticMoraleCard]:
        if isinstance(card, TroopCard):
            return self.remove_stack_troops(player, card.get_color(), card.get_troop())
        if isinstance(card, TacticMoraleCard):
            self.remove_stack_tacticmorales(player, card.get_tactics())
        raise ValueError(f"unknown card: {repr(card)}")

    def remove_stack_troops(
        self, player: int, color: Union[int, TroopColors], number: Union[int, Troops]
    ) -> Optional[TroopCard]:
        removal: Optional[TroopCard] = None
        for c in self.stacks[player]:
            if (
                isinstance(c, TroopCard)
                and c.get_color() == color
                and c.get_troop() == number
            ):
                removal = c
                break
        else:
            return None
        self.stacks[player].remove(removal)
        return removal

    def remove_stack_tacticmorales(
        self, player: int, tactic: Union[int, TacticMorales, Tactics]
    ) -> Optional[TacticMoraleCard]:
        removal: Optional[TacticMoraleCard] = None
        for c in self.stacks[player]:
            if isinstance(c, TacticMoraleCard) and c.get_tactics() == tactic:
                removal = c
                break
        else:
            return None
        self.stacks[player].remove(removal)
        return removal

    def add_env(self, player: int, card: TacticEnvironmentCard) -> None:
        self.envs[player].append(card)
        self.envs[player].sort()

    # Note: Remove the environment tactics is not allowed
    # def remove_env(
    #     self, player: int, env: Union[int, TacticEnvironments, Tactics]
    # ) -> Optional[TacticEnvironmentCard]:
    #    removal: Optional[TacticEnvironmentCard] = None
    #    for c in self.envs[player]:
    #        if c.get_tactics() == env:
    #            removal = c
    #            break
    #    else:
    #        return None
    #    self.envs[player].remove(removal)
    #    return removal

    def get_stacked_envs(self, player: int) -> Sequence[TacticEnvironmentCard]:
        return self.envs[player]

    def get_opposite_stacked_envs(self, player: int) -> Sequence[TacticEnvironmentCard]:
        return self.get_stacked_envs(PLAYER_A if player == PLAYER_B else PLAYER_B)

    def __repr__(self) -> str:
        side_a_cards = [""] * 3
        side_b_cards = [""] * 3
        side_a_envs = [""] * 2
        side_b_envs = [""] * 2
        flags = [" "] * 3
        for i, card in enumerate(self.get_stacked_cards(PLAYER_A)):
            side_a_cards[i] = repr(card)
        for i, card in enumerate(self.get_stacked_cards(PLAYER_B)):
            side_b_cards[i] = repr(card)
        for i, env in enumerate(self.get_stacked_envs(PLAYER_A)):
            side_a_envs[i] = repr(env)
        for i, env in enumerate(self.get_stacked_envs(PLAYER_B)):
            side_b_envs[i] = repr(env)
        flags[self.get_resolved() + 1] = "o"
        return _FLAG_REPRESENTATION_FORMAT.format(
            *side_a_cards, *side_a_envs, *side_b_cards, *side_b_envs, *flags
        )

    def __eq__(self, o: object) -> bool:
        return isinstance(o, Flag) and self.stacks == o.stacks

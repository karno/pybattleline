"""Battle Line Game System"""

import copy
import random
from typing import Generic, Iterable, List, Optional, TypeVar

from src.cards import (
    CardGenerator,
    TacticCard,
    TacticEnvironmentCard,
    TacticGuileCard,
    TroopAndTacticMoraleCard,
    TroopCard,
)

PLAYER_UNRESOLVED = -1
PLAYER_A = 0
PLAYER_B = 1

_FLAG_REPRESENTATION_FORMAT = """
 {9}
 {8}
--- {12} ---
 {7}
 {6}
 {5}
--- {10} ---
 {0}
 {1}
 {2}
--- {11} ---
 {3}
 {4}
"""


class Flag:
    @staticmethod
    def repr_flags(flags: Iterable["Flag"]) -> str:
        lines: List[str] = []
        for flag in flags:
            flag_lines = repr(flag).split("\n")
            for i, line in enumerate(flag_lines):
                if len(lines) < i:
                    lines[i] = line
                else:
                    lines[i] += line
        return "\n".join(lines)

    def __init__(self) -> None:
        self.side_A: List[TroopAndTacticMoraleCard] = []
        self.side_B: List[TroopAndTacticMoraleCard] = []
        self.side_A_env: List[TacticEnvironmentCard] = []
        self.side_B_env: List[TacticEnvironmentCard] = []
        self._flag_position = PLAYER_UNRESOLVED

    def get_stacked_cards(self, player: int) -> Iterable[TroopAndTacticMoraleCard]:
        if player == PLAYER_A:
            return self.side_A
        if player == PLAYER_B:
            return self.side_B
        raise ValueError(player)

    def get_stacked_envs(self, player: int) -> Iterable[TacticEnvironmentCard]:
        if player == PLAYER_A:
            return self.side_A_env
        if player == PLAYER_B:
            return self.side_B_env
        raise ValueError(player)

    def is_resolved(self) -> bool:
        return self._flag_position != PLAYER_UNRESOLVED

    def get_resolved(self) -> int:
        return self._flag_position

    def resolve(self, player: int) -> None:
        assert self._flag_position == PLAYER_UNRESOLVED, "the flag is already resolved!"
        self._flag_position = player

    def __repr__(self) -> str:
        side_a_cards: List[Optional[TroopAndTacticMoraleCard]] = [None] * 3
        side_b_cards: List[Optional[TroopAndTacticMoraleCard]] = [None] * 3
        side_a_envs: List[Optional[TacticEnvironmentCard]] = [None] * 2
        side_b_envs: List[Optional[TacticEnvironmentCard]] = [None] * 2
        flags = [" "] * 3
        for i, card in enumerate(self.get_stacked_cards(PLAYER_A)):
            side_a_cards[i] = card
        for i, card in enumerate(self.get_stacked_cards(PLAYER_B)):
            side_b_cards[i] = card
        for i, env in enumerate(self.get_stacked_envs(PLAYER_A)):
            side_a_envs[i] = env
        for i, env in enumerate(self.get_stacked_envs(PLAYER_B)):
            side_b_envs[i] = env
        flags[self.get_resolved() + 1] = "o"
        return _FLAG_REPRESENTATION_FORMAT.format(
            *side_a_cards, *side_a_envs, *side_b_cards, *side_b_envs, *flags
        )


TDeckCard = TypeVar("TDeckCard")


class Deck(Generic[TDeckCard]):
    def __init__(self, cards: Iterable[TDeckCard]) -> None:
        self._cards = list(cards)

    def shuffle(self) -> None:
        random.shuffle(self._cards)

    def draw(self) -> TDeckCard:
        return self._cards.pop()

    def is_remain(self) -> bool:
        return len(self._cards) > 0

    def __len__(self) -> int:
        return len(self._cards)

    def back(self, card: TDeckCard) -> None:
        self._cards.append(card)

    def __deepcopy__(self, _memo) -> "Deck[TDeckCard]":
        return Deck(self._cards[:])


class TroopsDeck(Deck[TroopCard]):
    @staticmethod
    def new() -> "TroopsDeck":
        return TroopsDeck(CardGenerator.troops())

    @staticmethod
    def shuffled() -> "TroopsDeck":
        t = TroopsDeck.new()
        t.shuffle()
        return t

    def __init__(self, cards=Iterable[TroopCard]) -> None:
        super().__init__(cards)

    def __deepcopy__(self, _memo) -> "TroopsDeck":
        return TroopsDeck(self._cards)


class TacticsDeck(Deck[TacticCard]):
    @staticmethod
    def new() -> "TacticsDeck":
        return TacticsDeck(CardGenerator.tactics())

    @staticmethod
    def shuffled() -> "TacticsDeck":
        t = TacticsDeck.new()
        t.shuffle()
        return t

    def __init__(self, cards=Iterable[TacticCard]) -> None:
        super().__init__(cards)

    def __deepcopy__(self, _memo) -> "TacticsDeck":
        return TacticsDeck(self._cards)


class GuileOperation:
    """Represent the operated tactics card and discarded troops card if existing."""

    def __init__(
        self, guile_card: TacticGuileCard, discarded_troop: Optional[TroopCard]
    ) -> None:
        self._guile_card = guile_card
        self._discarded = discarded_troop

    def get_guile_card(self) -> TacticGuileCard:
        return self._guile_card

    def get_discarded_troop_card(self) -> Optional[TroopCard]:
        return self._discarded

    def __repr__(self) -> str:
        text = repr(self._guile_card)
        if self._discarded:
            text += " | " + repr(self._guile_card)
        return text


class GameState:
    @staticmethod
    def new() -> "GameState":
        return GameState(
            TroopsDeck.shuffled(),
            TacticsDeck.shuffled(),
            [Flag() for _ in range(9)],
            [],
            [],
        )

    def __init__(
        self,
        troops_deck: TroopsDeck,
        tactics_deck: TacticsDeck,
        flags: Iterable[Flag],
        player_a_operations: List[GuileOperation],
        player_b_operations: List[GuileOperation],
    ) -> None:
        self._troops_deck = troops_deck
        self._tactics_deck = tactics_deck
        self._flags = list(flags)
        self._operations = [player_a_operations, player_b_operations]

    def get_troops_deck(self) -> TroopsDeck:
        return self._troops_deck

    def get_tactics_deck(self) -> TacticsDeck:
        return self._tactics_deck

    def get_flags(self) -> Iterable[Flag]:
        return self._flags

    def get_operations(self, player: int) -> List[GuileOperation]:
        return self._operations[player]

    def __deepcopy__(self, memo) -> "GameState":
        return GameState(
            copy.deepcopy(self._troops_deck, memo),
            copy.deepcopy(self._tactics_deck, memo),
            copy.deepcopy(self._flags, memo),
            copy.deepcopy(self._operations[PLAYER_A], memo),
            copy.deepcopy(self._operations[PLAYER_B], memo),
        )

    def get_winner(self) -> int:
        obtained_flags = [0] * 2
        continuously_obtained_flags = [0] * 2
        for flag in self._flags:
            state = flag.get_resolved()
            if state == PLAYER_UNRESOLVED:
                # flag is in play (not obtained)
                continuously_obtained_flags = [0] * 2
            else:
                continuously_obtained_flags[state] += 1
                obtained_flags[state] += 1
            for p in range(0, 2):
                if continuously_obtained_flags[p] >= 3 or obtained_flags[p] >= 5:
                    # player p is winner!
                    return p
        # game in play
        return PLAYER_UNRESOLVED

    def __repr__(self) -> str:
        text = ""
        # player b operations (in reverse)
        for op in reversed(self._operations[PLAYER_B]):
            text += repr(op)
        # flags
        Flag.repr_flags(self._flags)
        # player a operations
        for op in self._operations[PLAYER_A]:
            text += repr(op)
        return text

"""Battle Line Game System"""

import copy
import random
from src.cards import (
    CardGenerator,
    TacticCard,
    TacticEnvironmentCard,
    TroopAndTacticMoraleCard,
    TroopCard,
)
from typing import Generic, Iterable, List, TypeVar

PLAYER_UNRESOLVED = -1
PLAYER_A = 0
PLAYER_B = 1


class Flag:
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


class Grave:
    """Represent pair of discarded card and bound tactics card."""


class Graveyard:
    pass


class GameState:
    @staticmethod
    def new() -> "GameState":
        return GameState(
            TroopsDeck.shuffled(), TacticsDeck.shuffled(), [Flag() for _ in range(9)]
        )

    def __init__(
        self, troops_deck: TroopsDeck, tactics_deck: TacticsDeck, flags: Iterable[Flag]
    ) -> None:
        self._troops_deck = troops_deck
        self._tactics_deck = tactics_deck
        self._flags = list(flags)

    def get_troops_deck(self) -> TroopsDeck:
        return self._troops_deck

    def get_tactics_deck(self) -> TacticsDeck:
        return self._tactics_deck

    def get_flags(self) -> Iterable[Flag]:
        return self._flags

    def __deepcopy__(self, memo) -> "GameState":
        return GameState(
            copy.deepcopy(self._troops_deck, memo),
            copy.deepcopy(self._tactics_deck, memo),
            copy.deepcopy(self._flags, memo),
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

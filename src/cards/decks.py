"""Card decks definition."""

import random
from typing import Generic, Iterable, TypeVar

from src.cards.cards import CardGenerator, TacticCard, TroopCard

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

    def peek(self, num: int) -> Iterable[TDeckCard]:
        for i in range(num):
            yield self._cards[-(1 + i)]

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

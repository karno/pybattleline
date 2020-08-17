from src.game import GameState
from src.cards import CardType
from typing import Iterable


class Player:
    @staticmethod
    def __init__(self, hands: Iterable[CardType]) -> None:
        self._hands = list(hands)
        assert len(self._hands) == 7, "hands must be 7 cards."

    def play(self, game: GameState) -> GameState:
        pass

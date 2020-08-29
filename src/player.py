from src.game import GameState
from src.cards import Card
from typing import Iterable


class Player:
    def __init__(self, hands: Iterable[Card]) -> None:
        self._hands = list(hands)
        assert len(self._hands) == 7, "hands must be 7 cards."

    def play(self, game: GameState) -> GameState:

        pass

"""Battle Line Card Definitions."""

from abc import ABCMeta
import itertools
from src.cardtypes import (
    CardType,
    PlayedCardType,
    TacticEnvironments,
    TacticGuiles,
    TacticMorales,
    Tactics,
    TroopColors,
    Troops,
)
from typing import Iterable, Union


class Card(metaclass=ABCMeta):
    def get_card_type(self) -> CardType:
        raise NotImplementedError()


class PlayedCard(metaclass=ABCMeta):
    def get_played_type(self) -> PlayedCardType:
        raise NotImplementedError()


class TroopAndTacticMoraleCard(PlayedCard, metaclass=ABCMeta):
    def get_played_type(self) -> PlayedCardType:
        return PlayedCardType.TROOP_AND_MORALE_TACTICS


class TroopCard(Card, TroopAndTacticMoraleCard):
    def __init__(
        self, color: Union[TroopColors, int], number: Union[Troops, int]
    ) -> None:
        self._color = TroopColors(int(color))
        self._number = Troops(int(number))

    def get_card_type(self) -> CardType:
        return CardType.TROOP

    def get_troops(self) -> Troops:
        return self._number

    def get_color(self) -> TroopColors:
        return self._color


class TacticCard(Card, metaclass=ABCMeta):
    def __init__(self, value: Union[Tactics, int]) -> None:
        self._value = Tactics(int(value))

    def get_card_type(self) -> CardType:
        return CardType.TACTIC

    def get_tactics(self) -> Tactics:
        return self._value


class TacticMoraleCard(TacticCard, TroopAndTacticMoraleCard):
    def __init__(self, value: Union[TacticMorales, Tactics, int]) -> None:
        TacticCard.__init__(self, value)
        assert (
            self.get_tactics() in TacticMorales
        ), "value {} must be one of Leader (Alexander, Darius), Cavalry, or Shield.".format(
            self.get_tactics()
        )

    def get_played_type(self) -> PlayedCardType:
        return PlayedCardType.TROOP_AND_MORALE_TACTICS


class TacticEnvironmentCard(TacticCard, PlayedCard):
    def __init__(self, value: Union[TacticEnvironments, Tactics, int]) -> None:
        TacticCard.__init__(self, value)
        assert (
            self.get_tactics() in TacticEnvironments
        ), "value must be one of Leader (Alexander, Darius), Cavalry, or Shield."

    def get_played_type(self) -> PlayedCardType:
        return PlayedCardType.ENVIRONMENT_TACTICS


class TacticGuileCard(TacticCard, PlayedCard):
    def __init__(self, value: Union[TacticGuiles, Tactics, int]) -> None:
        TacticCard.__init__(self, value)
        assert (
            self.get_tactics() in TacticGuiles
        ), "value must be one of Leader (Alexander, Darius), Cavalry, or Shield."

    def get_played_type(self) -> PlayedCardType:
        return PlayedCardType.ENVIRONMENT_TACTICS


class CardGenerator:
    @staticmethod
    def troop(color: Union[TroopColors, int], number: Union[Troops, int]) -> TroopCard:
        return TroopCard(color, number)

    @staticmethod
    def tactic(value: Union[Tactics, int]) -> TacticCard:
        value = int(value)
        if value in TacticMorales:
            return TacticMoraleCard(value)
        if value in TacticEnvironments:
            return TacticEnvironmentCard(value)
        if value in TacticGuiles:
            return TacticGuileCard(value)
        raise ValueError(value)

    @staticmethod
    def troops() -> Iterable[TroopCard]:
        return [
            CardGenerator.troop(c, n) for c, n in itertools.product(TroopColors, Troops)
        ]

    @staticmethod
    def tactics() -> Iterable[TacticCard]:
        return [CardGenerator.tactic(t) for t in Tactics]

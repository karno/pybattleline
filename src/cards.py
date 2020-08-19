"""Battle Line Card Definitions."""

import itertools
from abc import ABCMeta
from typing import Iterable, Union

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

    def get_troop(self) -> Troops:
        return self._number

    def get_color(self) -> TroopColors:
        return self._color

    def __repr__(self) -> str:
        return f"[{self._color.name[0]}{int(self._number):02}]"


class TacticCard(Card, metaclass=ABCMeta):
    def __init__(self, value: Union[Tactics, int]) -> None:
        self._value = Tactics(int(value))

    def get_card_type(self) -> CardType:
        return CardType.TACTIC

    def get_tactics(self) -> Tactics:
        return self._value

    def __repr__(self) -> str:
        tactics_table = {
            Tactics.LEADER_ALEXANDER: "MLA",
            Tactics.LEADER_DARIUS: "MLD",
            Tactics.COMPANION_CAVALRY: "MCC",
            Tactics.SHIELD_BEARERS: "MSB",
            Tactics.FOG: "EFG",
            Tactics.MUD: "EMD",
            Tactics.SCOUT: "GSC",
            Tactics.REDEPLOY: "GRD",
            Tactics.DESERTER: "GDS",
            Tactics.TRAITOR: "GTR",
        }
        return f"<{tactics_table[self._value]}>"


class TacticMoraleCard(TacticCard, TroopAndTacticMoraleCard):
    def __init__(self, value: Union[TacticMorales, Tactics, int]) -> None:
        TacticCard.__init__(self, Tactics(int(value)))
        assert (
            self.get_tactics() in TacticMorales
        ), "value {} must be one of Leader (Alexander, Darius), Cavalry, or Shield.".format(
            self.get_tactics()
        )

    def get_played_type(self) -> PlayedCardType:
        return PlayedCardType.TROOP_AND_MORALE_TACTICS


class TacticEnvironmentCard(TacticCard, PlayedCard):
    def __init__(self, value: Union[TacticEnvironments, Tactics, int]) -> None:
        TacticCard.__init__(self, Tactics(int(value)))
        assert (
            self.get_tactics() in TacticEnvironments
        ), "value must be one of Fog or Mud."

    def get_played_type(self) -> PlayedCardType:
        return PlayedCardType.ENVIRONMENT_TACTICS


class TacticGuileCard(TacticCard, PlayedCard):
    def __init__(self, value: Union[TacticGuiles, Tactics, int]) -> None:
        TacticCard.__init__(self, Tactics(int(value)))
        assert (
            self.get_tactics() in TacticGuiles
        ), "value must be one of Scout, Redeploy, Deserter, or Traitor."

    def get_played_type(self) -> PlayedCardType:
        return PlayedCardType.GUILE_TACTICS


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

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
    """Game Card."""

    def get_card_type(self) -> CardType:
        raise NotImplementedError()


class PlayedCard(metaclass=ABCMeta):
    """Game Card in Playing Field."""

    def get_played_type(self) -> PlayedCardType:
        raise NotImplementedError()


class TroopAndTacticMoraleCard(PlayedCard, metaclass=ABCMeta):
    """Troops Card and Tactics Morales Card."""

    def get_played_type(self) -> PlayedCardType:
        return PlayedCardType.TROOP_AND_MORALE_TACTICS


class TroopCard(Card, TroopAndTacticMoraleCard):
    """Troop Card."""

    def __init__(
        self, color: Union[TroopColors, int], number: Union[Troops, int]
    ) -> None:  # noqa: D107
        self._color = TroopColors(int(color))
        self._number = Troops(int(number))

    def get_card_type(self) -> CardType:
        return CardType.TROOP

    def get_troop(self) -> Troops:
        return self._number

    def get_color(self) -> TroopColors:
        return self._color

    def __repr__(self) -> str:  # noqa: D105
        return f"[{self._color.name[0]}{int(self._number):02}]"

    def __eq__(self, other: object) -> bool:  # noqa: D105
        if isinstance(other, TacticCard):
            return False
        if not isinstance(other, TroopCard):
            return NotImplemented
        return (
            self.get_color() == other.get_color()
            and self.get_troop() == other.get_troop()
        )

    def __lt__(self, other: object) -> bool:  # noqa: D105
        if isinstance(other, TacticCard):
            # Troop < TacticMorale
            return True
        if not isinstance(other, TroopCard):
            return NotImplemented
        return (
            self.get_color() < other.get_color() or self.get_troop() < other.get_troop()
        )

    def __le__(self, other: object) -> bool:  # noqa: D105
        return self.__lt__(other) or self.__eq__(other)

    def __gt__(self, other: object) -> bool:  # noqa: D105
        return not self.__le__(other)

    def __ge__(self, other: object) -> bool:  # noqa: D105
        return not self.__lt__(other)


class TacticCard(Card, metaclass=ABCMeta):
    """Tactics Card."""

    def __init__(self, value: Union[Tactics, int]) -> None:  # noqa: D107
        self._value = Tactics(int(value))

    def get_card_type(self) -> CardType:
        return CardType.TACTIC

    def get_tactics(self) -> Tactics:
        return self._value

    def __repr__(self) -> str:  # noqa: D105: D105
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

    def __eq__(self, other: object) -> bool:  # noqa: D105: D105
        if isinstance(other, TroopCard):
            return False
        if not isinstance(other, TacticCard):
            return NotImplemented
        return self.get_tactics() == other.get_tactics()

    def __lt__(self, other: object) -> bool:  # noqa: D105: D105
        if isinstance(other, TroopCard):
            # Troop < TacticMorale
            return False
        if not isinstance(other, TacticCard):
            return NotImplemented
        return self.get_tactics() < other.get_tactics()

    def __le__(self, other: object) -> bool:  # noqa: D105: D105
        return self.__lt__(other) or self.__eq__(other)

    def __gt__(self, other: object) -> bool:  # noqa: D105: D105
        return not self.__le__(other)

    def __ge__(self, other: object) -> bool:  # noqa: D105
        return not self.__lt__(other)


class TacticMoraleCard(TacticCard, TroopAndTacticMoraleCard):
    """Tactics Morales Card."""

    def __init__(self, value: Union[TacticMorales, Tactics, int]) -> None:  # noqa: D107
        TacticCard.__init__(self, Tactics(int(value)))
        assert (
            self.get_tactics() in TacticMorales
        ), "value {} must be one of Leader (Alexander, Darius), Cavalry, or Shield.".format(
            self.get_tactics()
        )

    def get_played_type(self) -> PlayedCardType:
        return PlayedCardType.TROOP_AND_MORALE_TACTICS

    def get_tactic_morales(self) -> TacticMorales:
        return TacticMorales(int(self.get_tactics()))


class TacticEnvironmentCard(TacticCard, PlayedCard):
    """Tactics Environments Card."""

    def __init__(
        self, value: Union[TacticEnvironments, Tactics, int]
    ) -> None:  # noqa: D107
        TacticCard.__init__(self, Tactics(int(value)))
        assert (
            self.get_tactics() in TacticEnvironments
        ), "value must be one of Fog or Mud."

    def get_played_type(self) -> PlayedCardType:
        return PlayedCardType.ENVIRONMENT_TACTICS

    def get_tactic_envs(self) -> TacticEnvironments:
        return TacticEnvironments(int(self.get_tactics()))


class TacticGuileCard(TacticCard, PlayedCard):
    """Tactics Guiles Card."""

    def __init__(self, value: Union[TacticGuiles, Tactics, int]) -> None:  # noqa: D107
        TacticCard.__init__(self, Tactics(int(value)))
        assert (
            self.get_tactics() in TacticGuiles
        ), "value must be one of Scout, Redeploy, Deserter, or Traitor."

    def get_played_type(self) -> PlayedCardType:
        return PlayedCardType.GUILE_TACTICS

    def get_tactic_guiles(self) -> TacticGuiles:
        return TacticGuiles(int(self.get_tactics()))


class CardGenerator:
    """Game Card Generator."""

    @staticmethod
    def troop(color: Union[TroopColors, int], number: Union[Troops, int]) -> TroopCard:
        return TroopCard(color, number)

    @staticmethod
    def tactic(
        value: Union[TacticMorales, TacticEnvironments, TacticGuiles, Tactics, int]
    ) -> TacticCard:
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

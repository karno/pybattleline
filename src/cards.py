"""Battle Line Card Type Definitions"""

from enum import IntEnum, auto
import itertools
from typing import Iterable, Union


class CardType(IntEnum):
    TROOP = auto()
    TACTIC = auto()


class PlayedCardType(IntEnum):
    TROOP_AND_MORALE_TACTICS = auto()
    ENVIRONMENT_TACTICS = auto()
    GUILE_TACTICS = auto()


class TroopColors(IntEnum):
    """Define the troop colors.

    Every troop cards have one of the colors defined in this class.
    """

    RED = auto()
    ORANGE = auto()
    YELLOW = auto()
    GREEN = auto()
    BLUE = auto()
    PURPLE = auto()


class Troops(IntEnum):
    """Define the troop card entries.

    Every troop cards have one of the numbers defined in this class.
    Each card values could be mapped with integer numbers.
    e.g. Skirmishers (Troops.SKIRMISHERS) as 1.
    """

    SKIRMISHERS = auto()
    PELTASTS = auto()
    JAVALINEERS = auto()
    HOPLITES = auto()
    PHALANGISTS = auto()
    HYPASPISTS = auto()
    LIGHT_CAVALRY = auto()
    HEAVY_CAVALRY = auto()
    CHARIOTS = auto()
    ELEPHANTS = auto()


class Formations(IntEnum):
    """Define the formations of the cards.

    The values in this class can be compared with each other and
    the formation has higher value is stronger than the formation
    has smaller value.
    """

    HOST = auto()
    SKIRMISH_LINE = auto()
    BATTALION_ORDER = auto()
    PHALANX = auto()
    WEDGE = auto()


class Tactics(IntEnum):
    """Define the tactics card entries.

    Leaders: Behave as wildcards, but each players can
        play only one card of leaders during the single battle.
    Companion Cavalry: Behave as wild 8(Chariots) card.
        The color of this card will be defined when the flag is resolved.
    Shield Bearers: Behave as wild 1 to 3 card.
        The number and the color of this card will be defined when the flag is resolved.
    Fog: Disables all formations for the flag(any formations will be treated as hosts).
    Mud: Requires four cards for each side for the flag.
    Scout: You can draw a total three cards from one or both decks.
        After that, you choose two cards from your hand and return 
        them on the top of corresponding decks.
    Redeploy: You can choose one of any troop or tactics card deployed in your side next to
        unclaimed flag, then replace it into your another slot or discard it from the game.
    Deserter: You can choose one of any troop or tactics card deployed in opposite side next to
        unclaimed flag, then discard it from the game.
    Traitor: You can choose one of any troop or tactics card deployed in opposite side next to
        unclaimed flag, then replace it into your slot.
    """

    LEADER_ALEXANDER = auto()
    LEADER_DARIUS = auto()
    COMPANION_CAVALRY = auto()
    SHIELD_BEARERS = auto()
    FOG = auto()
    MUD = auto()
    SCOUT = auto()
    REDEPLOY = auto()
    DESERTER = auto()
    TRAITOR = auto()


class Card:
    def get_card_type(self) -> CardType:
        raise NotImplementedError()


class PlayedCard:
    def get_played_type(self) -> PlayedCardType:
        raise NotImplementedError()


class TroopAndTacticMoraleCard(PlayedCard):
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


class TacticCard(Card):
    def __init__(self, value: Union[Tactics, int]) -> None:
        self._value = Tactics(int(value))

    def get_card_type(self) -> CardType:
        return CardType.TACTIC

    def get_tactics(self) -> Tactics:
        return self._value


class TacticMoraleCard(TacticCard, TroopAndTacticMoraleCard):
    def __init__(self, value: Union[Tactics, int]) -> None:
        TacticCard.__init__(self, value)
        assert self.get_tactics() in (
            Tactics.LEADER_ALEXANDER,
            Tactics.LEADER_DARIUS,
            Tactics.COMPANION_CAVALRY,
            Tactics.SHIELD_BEARERS,
        ), "value must be one of Leader (Alexander, Darius), Cavalry, or Shield."

    def get_played_type(self) -> PlayedCardType:
        return PlayedCardType.TROOP_AND_MORALE_TACTICS


class TacticEnvironmentCard(TacticCard, PlayedCard):
    def __init__(self, value: Union[Tactics, int]) -> None:
        TacticCard.__init__(self, value)
        assert self.get_tactics() in (
            Tactics.FOG,
            Tactics.MUD,
        ), "value must be one of Leader (Alexander, Darius), Cavalry, or Shield."

    def get_played_type(self) -> PlayedCardType:
        return PlayedCardType.ENVIRONMENT_TACTICS


class TacticGuileCard(TacticCard, PlayedCard):
    def __init__(self, value: Union[Tactics, int]) -> None:
        TacticCard.__init__(self, value)
        assert self.get_tactics() in (
            Tactics.SCOUT,
            Tactics.REDEPLOY,
            Tactics.DESERTER,
            Tactics.TRAITOR,
        ), "value must be one of Leader (Alexander, Darius), Cavalry, or Shield."

    def get_played_type(self) -> PlayedCardType:
        return PlayedCardType.ENVIRONMENT_TACTICS


class CardGenerator:
    @staticmethod
    def troop(color: Union[TroopColors, int], number: Union[Troops, int]) -> TroopCard:
        return TroopCard(color, number)

    @staticmethod
    def tactic(value: Union[Tactics, int]) -> TacticCard:
        value = Tactics(int(value))
        if value in (
            Tactics.LEADER_ALEXANDER,
            Tactics.LEADER_DARIUS,
            Tactics.COMPANION_CAVALRY,
            Tactics.SHIELD_BEARERS,
        ):
            return TacticMoraleCard(value)
        if value in (Tactics.FOG, Tactics.MUD):
            return TacticEnvironmentCard(value)
        if value in (
            Tactics.SCOUT,
            Tactics.REDEPLOY,
            Tactics.DESERTER,
            Tactics.TRAITOR,
        ):
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

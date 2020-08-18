"""Battle Line Card Type Definitions."""

from enum import EnumMeta, IntEnum, auto


class CardType(IntEnum):
    """Define the card types."""

    TROOP = auto()
    TACTIC = auto()


class PlayedCardType(IntEnum):
    """Define the card types based on where it will be played on."""

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


class _TacticsEnumMeta(EnumMeta):
    def __contains__(self, other):
        if isinstance(
            other, (int, Tactics, TacticMorales, TacticEnvironments, TacticGuiles)
        ):
            try:
                self(int(other))
                return True
            except ValueError:
                return False
        super().__contains__(other)


class Tactics(IntEnum, metaclass=_TacticsEnumMeta):
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


class TacticMorales(IntEnum, metaclass=_TacticsEnumMeta):
    """Define the morale tactics card."""

    LEADER_ALEXANDER = Tactics.LEADER_ALEXANDER
    LEADER_DARIUS = Tactics.LEADER_DARIUS
    COMPANION_CAVALRY = Tactics.COMPANION_CAVALRY
    SHIELD_BEARERS = Tactics.SHIELD_BEARERS


class TacticEnvironments(IntEnum, metaclass=_TacticsEnumMeta):
    """Define the environment tactics card."""

    FOG = Tactics.FOG
    MUD = Tactics.MUD


class TacticGuiles(IntEnum, metaclass=_TacticsEnumMeta):
    """Define the guile tactics card."""

    SCOUT = Tactics.SCOUT
    REDEPLOY = Tactics.REDEPLOY
    DESERTER = Tactics.DESERTER
    TRAITOR = Tactics.TRAITOR


from src.cards import (
    CardGenerator,
    TacticCard,
    TacticEnvironmentCard,
    TacticGuileCard,
    TacticMoraleCard,
    TroopCard,
)
from src.cardtypes import (
    CardType,
    PlayedCardType,
    TacticEnvironments,
    TacticGuiles,
    TacticMorales,
    Tactics,
    TroopColors,
)


def test_valid_troop_card():
    card = CardGenerator.troop(TroopColors.RED, 3)
    assert card.get_color() == TroopColors.RED
    assert card.get_played_type() == PlayedCardType.TROOP_AND_MORALE_TACTICS
    assert card.get_troop() == 3


def test_valid_tactic_card():
    card = CardGenerator.tactic(Tactics.SCOUT)
    assert card.get_card_type() == CardType.TACTIC
    assert card.get_played_type() == PlayedCardType.GUILE_TACTICS
    assert card.get_tactics() == Tactics.SCOUT


def test_troop_card_repr():
    card = TroopCard(TroopColors.RED, 3)
    assert repr(card) == "[R03]"


def test_troop_card_repr_types():
    for c in TroopColors:
        c_id = c.name[0]
        card = TroopCard(c, 3)
        assert repr(card)[1] == c_id


def test_tactic_morale_card_type():
    card = TacticMoraleCard(Tactics.COMPANION_CAVALRY)
    assert card.get_played_type() == PlayedCardType.TROOP_AND_MORALE_TACTICS


def test_tactic_env_card_type():
    card = TacticEnvironmentCard(Tactics.FOG)
    assert card.get_played_type() == PlayedCardType.ENVIRONMENT_TACTICS


def test_tactic_guile_card_type():
    card = TacticGuileCard(Tactics.SCOUT)
    assert card.get_played_type() == PlayedCardType.GUILE_TACTICS


def test_tactic_card_repr():
    card = TacticCard(Tactics.COMPANION_CAVALRY)
    assert repr(card) == "<MCC>"


def test_tactic_morale_card_repr():
    card = TacticMoraleCard(Tactics.COMPANION_CAVALRY)
    assert repr(card) == "<MCC>"


def test_tactic_env_card_repr():
    card = TacticEnvironmentCard(Tactics.FOG)
    assert repr(card) == "<EFG>"


def test_tactic_guile_card_repr():
    card = TacticGuileCard(Tactics.SCOUT)
    assert repr(card) == "<GSC>"


def test_tactic_morale_card_repr_types():
    for t in TacticMorales:
        card = CardGenerator.tactic(t)
        assert repr(card)[1] == "M"


def test_tactic_env_card_repr_types():
    for t in TacticEnvironments:
        card = CardGenerator.tactic(t)
        assert repr(card)[1] == "E"


def test_tactic_guile_card_repr_types():
    for t in TacticGuiles:
        card = CardGenerator.tactic(t)
        assert repr(card)[1] == "G"

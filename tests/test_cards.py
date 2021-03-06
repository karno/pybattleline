# noqa


from src.cards.cards import (
    CardGenerator,
    TacticCard,
    TacticEnvironmentCard,
    TacticGuileCard,
    TacticMoraleCard,
    TroopCard,
)
from src.cards.cardtypes import (
    CardType,
    PlayedCardType,
    TacticEnvironments,
    TacticGuiles,
    TacticMorales,
    Tactics,
    TroopColors,
)


def test_valid_troop_card():  # noqa
    card = CardGenerator.troop(TroopColors.RED, 3)
    assert card.get_color() == TroopColors.RED
    assert card.get_played_type() == PlayedCardType.TROOP_AND_MORALE_TACTICS
    assert card.get_troop() == 3


def test_valid_tactic_card():  # noqa
    card = CardGenerator.tactic(Tactics.SCOUT)
    assert card.get_card_type() == CardType.TACTIC
    assert card.get_played_type() == PlayedCardType.GUILE_TACTICS
    assert card.get_tactics() == Tactics.SCOUT


def test_troop_card_repr():  # noqa
    card = TroopCard(TroopColors.RED, 3)
    assert repr(card) == "[R03]"


def test_troop_card_repr_types():  # noqa
    for c in TroopColors:
        c_id = c.name[0]
        card = TroopCard(c, 3)
        assert repr(card)[1] == c_id


def test_tactic_morale_card_type():  # noqa
    card = TacticMoraleCard(Tactics.COMPANION_CAVALRY)
    assert card.get_played_type() == PlayedCardType.TROOP_AND_MORALE_TACTICS


def test_tactic_env_card_type():  # noqa
    card = TacticEnvironmentCard(Tactics.FOG)
    assert card.get_played_type() == PlayedCardType.ENVIRONMENT_TACTICS


def test_tactic_guile_card_type():  # noqa
    card = TacticGuileCard(Tactics.SCOUT)
    assert card.get_played_type() == PlayedCardType.GUILE_TACTICS


def test_tactic_card_repr():  # noqa
    card = TacticCard(Tactics.COMPANION_CAVALRY)
    assert repr(card) == "<MCC>"


def test_tactic_morale_card_repr():  # noqa
    card = TacticMoraleCard(Tactics.COMPANION_CAVALRY)
    assert repr(card) == "<MCC>"


def test_tactic_env_card_repr():  # noqa
    card = TacticEnvironmentCard(Tactics.FOG)
    assert repr(card) == "<EFG>"


def test_tactic_guile_card_repr():  # noqa
    card = TacticGuileCard(Tactics.SCOUT)
    assert repr(card) == "<GSC>"


def test_tactic_morale_card_repr_types():  # noqa
    for t in TacticMorales:
        card = CardGenerator.tactic(t)
        assert repr(card)[1] == "M"


def test_tactic_env_card_repr_types():  # noqa
    for t in TacticEnvironments:
        card = CardGenerator.tactic(t)
        assert repr(card)[1] == "E"


def test_tactic_guile_card_repr_types():  # noqa
    for t in TacticGuiles:
        card = CardGenerator.tactic(t)
        assert repr(card)[1] == "G"

# noqa


from src.cards.cardtypes import TacticEnvironments, TacticGuiles, TacticMorales, Tactics


def test_card_definition_tactics():  # noqa
    assert Tactics.LEADER_ALEXANDER == Tactics.LEADER_ALEXANDER


def test_card_definition_tacticmorales():  # noqa
    assert TacticMorales.LEADER_ALEXANDER == TacticMorales.LEADER_ALEXANDER


def test_card_definition_each_other():  # noqa
    assert TacticMorales.LEADER_ALEXANDER == Tactics.LEADER_ALEXANDER


def test_card_compatibility_morales():  # noqa
    assert TacticMorales.LEADER_ALEXANDER in Tactics


def test_card_compatibility_morales_rev():  # noqa
    assert Tactics.LEADER_ALEXANDER in TacticMorales


def test_card_compatibility_morales_negative():  # noqa
    assert Tactics.FOG not in TacticMorales


def test_card_compatibility_envs():  # noqa
    assert TacticEnvironments.FOG in Tactics


def test_card_compatibility_envs_rev():  # noqa
    assert Tactics.FOG in TacticEnvironments


def test_card_compatibility_envs_negative():  # noqa
    assert Tactics.SCOUT not in TacticEnvironments


def test_card_compatibility_guiles():  # noqa
    assert TacticGuiles.SCOUT in Tactics


def test_card_compatibility_guiles_rev():  # noqa
    assert Tactics.SCOUT in TacticGuiles


def test_card_compatibility_guiles_negative():  # noqa
    assert Tactics.LEADER_ALEXANDER not in TacticGuiles

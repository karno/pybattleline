from src.cardtypes import TacticEnvironments, TacticGuiles, TacticMorales, Tactics


def test_card_definition_tactics():
    assert Tactics.LEADER_ALEXANDER == Tactics.LEADER_ALEXANDER


def test_card_definition_tacticmorales():
    assert TacticMorales.LEADER_ALEXANDER == TacticMorales.LEADER_ALEXANDER


def test_card_definition_each_other():
    assert TacticMorales.LEADER_ALEXANDER == Tactics.LEADER_ALEXANDER


def test_card_compatibility_morales():
    assert TacticMorales.LEADER_ALEXANDER in Tactics


def test_card_compatibility_morales_rev():
    assert Tactics.LEADER_ALEXANDER in TacticMorales


def test_card_compatibility_morales_negative():
    assert Tactics.FOG not in TacticMorales


def test_card_compatibility_envs():
    assert TacticEnvironments.FOG in Tactics


def test_card_compatibility_envs_rev():
    assert Tactics.FOG in TacticEnvironments


def test_card_compatibility_envs_negative():
    assert Tactics.SCOUT not in TacticEnvironments


def test_card_compatibility_guiles():
    assert TacticGuiles.SCOUT in Tactics


def test_card_compatibility_guiles_rev():
    assert Tactics.SCOUT in TacticGuiles


def test_card_compatibility_guiles_negative():
    assert Tactics.LEADER_ALEXANDER not in TacticGuiles

# noqa

from src.cardtypes import TacticEnvironments, TacticMorales, Tactics, TroopColors
from src.cards import CardGenerator
from src.game import Flag, PLAYER_A, PLAYER_B
from src import game


def test_flag_stack_troop():  # noqa
    flag = Flag()
    c_r3 = CardGenerator.troop(TroopColors.RED, 3)
    flag.add_stack(PLAYER_A, c_r3)
    assert len(flag.get_stacked_cards(PLAYER_A)) == 1
    assert flag.remove_stack_troops(PLAYER_A, TroopColors.RED, 3) == c_r3


def test_flag_stack_tacticmorales():  # noqa
    flag = Flag()
    c_ld = CardGenerator.tactic(Tactics.LEADER_DARIUS)
    flag.add_stack(PLAYER_B, c_ld)
    assert len(flag.get_stacked_cards(PLAYER_B)) == 1
    assert (
        flag.remove_stack_tacticmorales(PLAYER_B, TacticMorales.LEADER_DARIUS) == c_ld
    )


def test_flag_env():  # noqa
    flag = Flag()
    c_mud = CardGenerator.tactic(Tactics.MUD)
    flag.add_env(PLAYER_A, c_mud)
    assert len(flag.get_stacked_envs(PLAYER_A)) == 1
    assert flag.remove_env(PLAYER_A, TacticEnvironments.MUD) == c_mud


def test_troops_deck_len():  # noqa
    assert len(game.TroopsDeck.new()) == 60


def test_tactics_deck_len():  # noqa
    assert len(game.TacticsDeck.new()) == 10


def test_flag_deepcopy():  # noqa
    flag = Flag()
    c_r3 = CardGenerator.troop(TroopColors.RED, 3)
    flag.add_stack(PLAYER_A, c_r3)
    c_ld = CardGenerator.tactic(Tactics.LEADER_DARIUS)
    flag.add_stack(PLAYER_B, c_ld)


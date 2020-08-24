# noqa
from src.cardtypes import TroopColors
from src.cards import CardGenerator
from src.resolver import check_resolve
from src.game import Flag, GameState, PLAYER_A, PLAYER_B, PLAYER_UNRESOLVED


def test_resolve_unresolvable():  # noqa
    state = GameState.new()
    flag: Flag = state.get_flags()[0]
    assert check_resolve(flag, state) == PLAYER_UNRESOLVED
    flag.add_stack(PLAYER_A, CardGenerator.troop(TroopColors.RED, 3))
    assert flag.get_last_stacked_player() == PLAYER_A
    assert len(flag.get_stacked_cards(PLAYER_A)) == 1
    assert len(flag.get_stacked_cards(PLAYER_B)) == 0
    assert check_resolve(flag, state) == PLAYER_UNRESOLVED

    flag.add_stack(PLAYER_A, CardGenerator.troop(TroopColors.RED, 4))
    assert flag.get_last_stacked_player() == PLAYER_A
    assert len(flag.get_stacked_cards(PLAYER_A)) == 2
    assert len(flag.get_stacked_cards(PLAYER_B)) == 0
    assert check_resolve(flag, state) == PLAYER_UNRESOLVED

    flag.add_stack(PLAYER_A, CardGenerator.troop(TroopColors.RED, 5))
    assert flag.get_last_stacked_player() == PLAYER_A
    assert len(flag.get_stacked_cards(PLAYER_A)) == 3
    assert len(flag.get_stacked_cards(PLAYER_B)) == 0
    assert check_resolve(flag, state) == PLAYER_UNRESOLVED

    flag.add_stack(PLAYER_B, CardGenerator.troop(TroopColors.BLUE, 4))
    assert flag.get_last_stacked_player() == PLAYER_B
    assert len(flag.get_stacked_cards(PLAYER_A)) == 3
    assert len(flag.get_stacked_cards(PLAYER_B)) == 1
    assert check_resolve(flag, state) == PLAYER_UNRESOLVED

    flag.add_stack(PLAYER_B, CardGenerator.troop(TroopColors.BLUE, 5))
    assert flag.get_last_stacked_player() == PLAYER_B
    assert len(flag.get_stacked_cards(PLAYER_A)) == 3
    assert len(flag.get_stacked_cards(PLAYER_B)) == 2
    assert check_resolve(flag, state) == PLAYER_UNRESOLVED

    flag.remove_stack_troops(PLAYER_A, TroopColors.RED, 3)
    assert flag.get_last_stacked_player() == PLAYER_B
    assert len(flag.get_stacked_cards(PLAYER_A)) == 2
    assert len(flag.get_stacked_cards(PLAYER_B)) == 2
    assert check_resolve(flag, state) == PLAYER_UNRESOLVED

    flag.add_stack(PLAYER_B, CardGenerator.troop(TroopColors.BLUE, 6))
    assert flag.get_last_stacked_player() == PLAYER_B
    assert len(flag.get_stacked_cards(PLAYER_A)) == 2
    assert len(flag.get_stacked_cards(PLAYER_B)) == 3
    assert check_resolve(flag, state) == PLAYER_UNRESOLVED

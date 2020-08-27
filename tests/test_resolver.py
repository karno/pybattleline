# noqa
from src.cardtypes import TacticMorales, TroopColors
from src.cards import CardGenerator, TroopCard
from src.resolver import (
    aggregate_used_troops,
    check_resolvable_for_single_flag,
    possible_maximum_strength_for_battalion,
    possible_maximum_strength_for_host,
    possible_maximum_strength_for_phalanx,
    possible_maximum_strength_for_skirmish,
    possible_maximum_strength_for_wedge,
)
from src.game import Flag, GameState, PLAYER_A, PLAYER_B, PLAYER_UNRESOLVED


def test_resolve_unresolvable():  # noqa: D103
    state = GameState.new()
    flag: Flag = state.get_flags()[0]
    assert _check_resolve(flag, state) == PLAYER_UNRESOLVED
    flag.add_stack(PLAYER_A, CardGenerator.troop(TroopColors.RED, 3))
    assert flag.get_last_stacked_player() == PLAYER_A
    assert len(flag.get_stacked_cards(PLAYER_A)) == 1
    assert len(flag.get_stacked_cards(PLAYER_B)) == 0
    assert _check_resolve(flag, state) == PLAYER_UNRESOLVED

    flag.add_stack(PLAYER_A, CardGenerator.troop(TroopColors.RED, 4))
    assert flag.get_last_stacked_player() == PLAYER_A
    assert len(flag.get_stacked_cards(PLAYER_A)) == 2
    assert len(flag.get_stacked_cards(PLAYER_B)) == 0
    assert _check_resolve(flag, state) == PLAYER_UNRESOLVED

    flag.add_stack(PLAYER_A, CardGenerator.troop(TroopColors.RED, 5))
    assert flag.get_last_stacked_player() == PLAYER_A
    assert len(flag.get_stacked_cards(PLAYER_A)) == 3
    assert len(flag.get_stacked_cards(PLAYER_B)) == 0
    assert _check_resolve(flag, state) == PLAYER_UNRESOLVED

    flag.add_stack(PLAYER_B, CardGenerator.troop(TroopColors.BLUE, 4))
    assert flag.get_last_stacked_player() == PLAYER_B
    assert len(flag.get_stacked_cards(PLAYER_A)) == 3
    assert len(flag.get_stacked_cards(PLAYER_B)) == 1
    assert _check_resolve(flag, state) == PLAYER_UNRESOLVED

    flag.add_stack(PLAYER_B, CardGenerator.troop(TroopColors.BLUE, 5))
    assert flag.get_last_stacked_player() == PLAYER_B
    assert len(flag.get_stacked_cards(PLAYER_A)) == 3
    assert len(flag.get_stacked_cards(PLAYER_B)) == 2
    assert _check_resolve(flag, state) == PLAYER_UNRESOLVED

    flag.remove_stack_troops(PLAYER_A, TroopColors.RED, 3)
    assert flag.get_last_stacked_player() == PLAYER_B
    assert len(flag.get_stacked_cards(PLAYER_A)) == 2
    assert len(flag.get_stacked_cards(PLAYER_B)) == 2
    assert _check_resolve(flag, state) == PLAYER_UNRESOLVED

    flag.add_stack(PLAYER_B, CardGenerator.troop(TroopColors.BLUE, 6))
    assert flag.get_last_stacked_player() == PLAYER_B
    assert len(flag.get_stacked_cards(PLAYER_A)) == 2
    assert len(flag.get_stacked_cards(PLAYER_B)) == 3
    assert _check_resolve(flag, state) == PLAYER_UNRESOLVED


def test_solve_wedge():  # noqa: D103
    stack = [
        CardGenerator.troop(TroopColors.RED, 3),
        CardGenerator.troop(TroopColors.RED, 4),
        CardGenerator.troop(TroopColors.RED, 5),
    ]
    used_cards = [c for c in stack if isinstance(c, TroopCard)]
    strength, solved = possible_maximum_strength_for_wedge(stack, 3, used_cards)
    assert strength == sum([3, 4, 5])
    assert solved


def test_solve_wedge_negative():  # noqa: D103
    stack = [
        CardGenerator.troop(TroopColors.RED, 3),
        CardGenerator.troop(TroopColors.RED, 4),
        CardGenerator.troop(TroopColors.RED, 6),
    ]
    used_cards = [c for c in stack if isinstance(c, TroopCard)]
    strength, solved = possible_maximum_strength_for_wedge(stack, 3, used_cards)
    assert strength == 0
    assert not solved


def test_solve_wedge_possible_0():  # noqa: D103
    stack = []
    used_cards = [c for c in stack if isinstance(c, TroopCard)]
    strength, solved = possible_maximum_strength_for_wedge(stack, 3, used_cards)
    assert strength == sum([8, 9, 10])
    assert not solved


def test_solve_wedge_possible_1():  # noqa: D103
    stack = [
        CardGenerator.troop(TroopColors.RED, 3),
    ]
    used_cards = [c for c in stack if isinstance(c, TroopCard)]
    strength, solved = possible_maximum_strength_for_wedge(stack, 3, used_cards)
    assert strength == sum([3, 4, 5])
    assert not solved


def test_solve_wedge_possible_2():  # noqa: D103
    stack = [
        CardGenerator.troop(TroopColors.RED, 3),
        CardGenerator.troop(TroopColors.RED, 4),
    ]
    used_cards = [c for c in stack if isinstance(c, TroopCard)]
    strength, solved = possible_maximum_strength_for_wedge(stack, 3, used_cards)
    assert strength == sum([3, 4, 5])
    assert not solved


def test_solve_wedge_inpossible():  # noqa: D103
    stack = [
        CardGenerator.troop(TroopColors.RED, 3),
        CardGenerator.troop(TroopColors.RED, 4),
    ]
    used_cards = [c for c in stack if isinstance(c, TroopCard)]
    used_cards.extend(
        [
            CardGenerator.troop(TroopColors.RED, 2),
            CardGenerator.troop(TroopColors.RED, 5),
        ]
    )
    strength, solved = possible_maximum_strength_for_wedge(stack, 3, used_cards)
    assert strength == 0
    assert not solved


def test_solve_wedge_wild():  # noqa: D103
    stack = [
        CardGenerator.troop(TroopColors.RED, 3),
        CardGenerator.troop(TroopColors.RED, 4),
        CardGenerator.tactic(TacticMorales.LEADER_ALEXANDER),
    ]
    used_cards = [c for c in stack if isinstance(c, TroopCard)]
    strength, solved = possible_maximum_strength_for_wedge(stack, 3, used_cards)
    assert strength == sum([3, 4, 5])
    assert solved


def test_solve_wedge_shield():  # noqa: D103
    stack = [
        CardGenerator.troop(TroopColors.RED, 3),
        CardGenerator.troop(TroopColors.RED, 4),
        CardGenerator.tactic(TacticMorales.SHIELD_BEARERS),
    ]
    used_cards = [c for c in stack if isinstance(c, TroopCard)]
    strength, solved = possible_maximum_strength_for_wedge(stack, 3, used_cards)
    assert strength == sum([2, 3, 4])
    assert solved


def test_solve_wedge_cavalry_and_wild():  # noqa: D103
    stack = [
        CardGenerator.tactic(TacticMorales.LEADER_ALEXANDER),
        CardGenerator.tactic(TacticMorales.COMPANION_CAVALRY),
        CardGenerator.troop(TroopColors.RED, 9),
    ]
    used_cards = [c for c in stack if isinstance(c, TroopCard)]
    strength, solved = possible_maximum_strength_for_wedge(stack, 3, used_cards)
    assert strength == sum([8, 9, 10])
    assert solved


def test_solve_phalanx():  # noqa: D103
    stack = [
        CardGenerator.troop(TroopColors.RED, 9),
        CardGenerator.troop(TroopColors.BLUE, 9),
        CardGenerator.troop(TroopColors.GREEN, 9),
    ]
    used_cards = [c for c in stack if isinstance(c, TroopCard)]
    strength, solved = possible_maximum_strength_for_phalanx(stack, 3, used_cards)
    assert strength == 9 * 3
    assert solved


def test_solve_phalanx_negative():  # noqa: D103
    stack = [
        CardGenerator.troop(TroopColors.RED, 9),
        CardGenerator.troop(TroopColors.BLUE, 9),
        CardGenerator.troop(TroopColors.GREEN, 10),
    ]
    used_cards = [c for c in stack if isinstance(c, TroopCard)]
    strength, solved = possible_maximum_strength_for_phalanx(stack, 3, used_cards)
    assert strength == 0
    assert not solved


def test_solve_phalanx_possible_0():  # noqa: D103
    stack = []
    used_cards = [c for c in stack if isinstance(c, TroopCard)]
    strength, solved = possible_maximum_strength_for_phalanx(stack, 3, used_cards)
    assert strength == 10 * 3
    assert not solved


def test_solve_phalanx_possible_1():  # noqa: D103
    stack = [
        CardGenerator.troop(TroopColors.RED, 9),
    ]
    used_cards = [c for c in stack if isinstance(c, TroopCard)]
    strength, solved = possible_maximum_strength_for_phalanx(stack, 3, used_cards)
    assert strength == 9 * 3
    assert not solved


def test_solve_phalanx_possible_2():  # noqa: D103
    stack = [
        CardGenerator.troop(TroopColors.RED, 9),
        CardGenerator.troop(TroopColors.BLUE, 9),
    ]
    used_cards = [c for c in stack if isinstance(c, TroopCard)]
    strength, solved = possible_maximum_strength_for_phalanx(stack, 3, used_cards)
    assert strength == 9 * 3
    assert not solved


def test_solve_phalanx_inpossible():  # noqa: D103
    stack = [
        CardGenerator.troop(TroopColors.RED, 9),
        CardGenerator.troop(TroopColors.BLUE, 9),
    ]
    # used_cards = [c for c in stack if isinstance(c, TroopCard)]
    used_cards = [CardGenerator.troop(c, 9) for c in TroopColors]
    strength, solved = possible_maximum_strength_for_phalanx(stack, 3, used_cards)
    assert strength == 0
    assert not solved


def test_solve_phalanx_wild():  # noqa: D103
    stack = [
        CardGenerator.troop(TroopColors.YELLOW, 9),
        CardGenerator.tactic(TacticMorales.LEADER_DARIUS),
        CardGenerator.troop(TroopColors.GREEN, 9),
    ]
    used_cards = [c for c in stack if isinstance(c, TroopCard)]
    strength, solved = possible_maximum_strength_for_phalanx(stack, 3, used_cards)
    assert strength == 9 * 3
    assert solved


def test_solve_battalion():  # noqa: D103
    stack = [
        CardGenerator.troop(TroopColors.YELLOW, 9),
        CardGenerator.troop(TroopColors.YELLOW, 3),
        CardGenerator.troop(TroopColors.YELLOW, 1),
    ]
    used_cards = [c for c in stack if isinstance(c, TroopCard)]
    strength, solved = possible_maximum_strength_for_battalion(stack, 3, used_cards)
    assert strength == sum([9, 3, 1])
    assert solved


def test_solve_battalion_negative():  # noqa: D103
    stack = [
        CardGenerator.troop(TroopColors.YELLOW, 9),
        CardGenerator.troop(TroopColors.YELLOW, 3),
        CardGenerator.troop(TroopColors.BLUE, 1),
    ]
    used_cards = [c for c in stack if isinstance(c, TroopCard)]
    strength, solved = possible_maximum_strength_for_battalion(stack, 3, used_cards)
    assert strength == 0
    assert not solved


def test_solve_battalion_possible_0():  # noqa: D103
    stack = []
    used_cards = [c for c in stack if isinstance(c, TroopCard)]
    strength, solved = possible_maximum_strength_for_battalion(stack, 3, used_cards)
    assert strength == sum([10, 9, 8])
    assert not solved


def test_solve_battalion_possible_1():  # noqa: D103
    stack = [
        CardGenerator.troop(TroopColors.YELLOW, 9),
    ]
    used_cards = [c for c in stack if isinstance(c, TroopCard)]
    strength, solved = possible_maximum_strength_for_battalion(stack, 3, used_cards)
    assert strength == sum([10, 9, 8])
    assert not solved


def test_solve_battalion_possible_2():  # noqa: D103
    stack = [
        CardGenerator.troop(TroopColors.YELLOW, 1),
        CardGenerator.troop(TroopColors.YELLOW, 9),
    ]
    used_cards = [c for c in stack if isinstance(c, TroopCard)]
    strength, solved = possible_maximum_strength_for_battalion(stack, 3, used_cards)
    assert strength == sum([10, 9, 1])
    assert not solved


def test_solve_battalion_inpossible():  # noqa: D103
    stack = [
        CardGenerator.troop(TroopColors.YELLOW, 1),
        CardGenerator.troop(TroopColors.YELLOW, 9),
    ]
    used_cards = [CardGenerator.troop(TroopColors.YELLOW, n) for n in range(1, 11)]
    strength, solved = possible_maximum_strength_for_battalion(stack, 3, used_cards)
    assert strength == 0
    assert not solved


def test_solve_skirmish():  # noqa: D103
    stack = [
        CardGenerator.troop(TroopColors.RED, 2),
        CardGenerator.troop(TroopColors.YELLOW, 1),
        CardGenerator.troop(TroopColors.GREEN, 3),
    ]
    used_cards = [c for c in stack if isinstance(c, TroopCard)]
    strength, solved = possible_maximum_strength_for_skirmish(stack, 3, used_cards)
    assert strength == sum([1, 2, 3])
    assert solved


def test_solve_skirmish_negative():  # noqa: D103
    stack = [
        CardGenerator.troop(TroopColors.RED, 2),
        CardGenerator.troop(TroopColors.YELLOW, 1),
        CardGenerator.troop(TroopColors.GREEN, 4),
    ]
    used_cards = [c for c in stack if isinstance(c, TroopCard)]
    strength, solved = possible_maximum_strength_for_skirmish(stack, 3, used_cards)
    assert strength == 0
    assert not solved


def test_solve_skirmish_possible_0():  # noqa: D103
    stack = []
    used_cards = [c for c in stack if isinstance(c, TroopCard)]
    strength, solved = possible_maximum_strength_for_skirmish(stack, 3, used_cards)
    assert strength == sum([8, 9, 10])
    assert not solved


def test_solve_skirmish_possible_1():  # noqa: D103
    stack = [
        CardGenerator.troop(TroopColors.YELLOW, 1),
    ]
    used_cards = [c for c in stack if isinstance(c, TroopCard)]
    strength, solved = possible_maximum_strength_for_skirmish(stack, 3, used_cards)
    assert strength == sum([1, 2, 3])
    assert not solved


def test_solve_skirmish_possible_2():  # noqa: D103
    stack = [
        CardGenerator.troop(TroopColors.YELLOW, 1),
        CardGenerator.troop(TroopColors.GREEN, 3),
    ]
    used_cards = [c for c in stack if isinstance(c, TroopCard)]
    strength, solved = possible_maximum_strength_for_skirmish(stack, 3, used_cards)
    assert strength == sum([1, 2, 3])
    assert not solved


def test_solve_skirmish_inpossible():  # noqa: D103
    stack = [
        CardGenerator.troop(TroopColors.YELLOW, 1),
        CardGenerator.troop(TroopColors.GREEN, 3),
    ]
    used_cards = [c for c in stack if isinstance(c, TroopCard)]
    used_cards.extend([CardGenerator.troop(c, 2) for c in TroopColors])
    strength, solved = possible_maximum_strength_for_skirmish(stack, 3, used_cards)
    assert strength == 0
    assert not solved


def test_solve_host():  # noqa: D103
    stack = [
        CardGenerator.troop(TroopColors.YELLOW, 1),
        CardGenerator.troop(TroopColors.GREEN, 3),
        CardGenerator.troop(TroopColors.YELLOW, 8),
    ]
    used_cards = [c for c in stack if isinstance(c, TroopCard)]
    strength, solved = possible_maximum_strength_for_host(stack, 3, used_cards)
    assert strength == sum([1, 3, 8])
    assert solved


def test_solve_host_negative():  # noqa: D103
    # any 3 cards are OK, so this test case is empty
    assert True


def test_solve_host_possible_0():  # noqa: D103
    stack = []
    used_cards = [c for c in stack if isinstance(c, TroopCard)]
    strength, solved = possible_maximum_strength_for_host(stack, 3, used_cards)
    assert strength == sum([10, 10, 10])
    assert not solved


def test_solve_host_possible_1():  # noqa: D103
    stack = [
        CardGenerator.troop(TroopColors.YELLOW, 1),
    ]
    used_cards = [c for c in stack if isinstance(c, TroopCard)]
    strength, solved = possible_maximum_strength_for_host(stack, 3, used_cards)
    assert strength == sum([1, 10, 10])
    assert not solved


def test_solve_host_possible_2():  # noqa: D103
    stack = [
        CardGenerator.troop(TroopColors.YELLOW, 1),
        CardGenerator.troop(TroopColors.GREEN, 3),
    ]
    used_cards = [c for c in stack if isinstance(c, TroopCard)]
    strength, solved = possible_maximum_strength_for_host(stack, 3, used_cards)
    assert strength == sum([1, 3, 10])
    assert not solved


def test_solve_host_possible_2_limited():  # noqa: D103
    stack = [
        CardGenerator.troop(TroopColors.YELLOW, 1),
        CardGenerator.troop(TroopColors.GREEN, 3),
    ]
    used_cards = [c for c in stack if isinstance(c, TroopCard)]
    used_cards.extend([CardGenerator.troop(c, 10) for c in TroopColors])
    strength, solved = possible_maximum_strength_for_host(stack, 3, used_cards)
    assert strength == sum([1, 3, 9])
    assert not solved


def test_solve_host_inpossible():  # noqa: D103
    stack = [
        CardGenerator.troop(TroopColors.YELLOW, 1),
        CardGenerator.troop(TroopColors.GREEN, 3),
    ]

    # used_cards = [c for c in stack if isinstance(c, TroopCard)]
    used_cards = [CardGenerator.troop(c, n) for c in TroopColors for n in range(1, 11)]
    strength, solved = possible_maximum_strength_for_host(stack, 3, used_cards)
    assert strength == 0
    assert not solved


def test_solve_wedge_vs_phalanx():  # noqa: D103
    state = GameState.new()
    flag: Flag = state.get_flags()[0]
    flag.add_stack(PLAYER_A, CardGenerator.troop(TroopColors.RED, 3))
    flag.add_stack(PLAYER_A, CardGenerator.troop(TroopColors.RED, 4))
    flag.add_stack(PLAYER_A, CardGenerator.troop(TroopColors.RED, 2))
    flag.add_stack(PLAYER_B, CardGenerator.troop(TroopColors.BLUE, 8))
    flag.add_stack(PLAYER_B, CardGenerator.troop(TroopColors.GREEN, 8))
    flag.add_stack(PLAYER_B, CardGenerator.troop(TroopColors.YELLOW, 8))
    assert _check_resolve(flag, state) == PLAYER_A


def test_solve_wedge_vs_wedge():  # noqa: D103
    state = GameState.new()
    flag: Flag = state.get_flags()[0]
    flag.add_stack(PLAYER_A, CardGenerator.troop(TroopColors.RED, 3))
    flag.add_stack(PLAYER_A, CardGenerator.troop(TroopColors.RED, 1))
    flag.add_stack(PLAYER_A, CardGenerator.troop(TroopColors.RED, 2))
    flag.add_stack(PLAYER_B, CardGenerator.troop(TroopColors.BLUE, 8))
    flag.add_stack(PLAYER_B, CardGenerator.troop(TroopColors.BLUE, 9))
    flag.add_stack(PLAYER_B, CardGenerator.troop(TroopColors.BLUE, 10))
    assert _check_resolve(flag, state) == PLAYER_B


def test_solve_wild_wedge_vs_wedge():  # noqa: D103
    state = GameState.new()
    flag: Flag = state.get_flags()[0]
    flag.add_stack(PLAYER_A, CardGenerator.troop(TroopColors.RED, 3))
    flag.add_stack(PLAYER_A, CardGenerator.troop(TroopColors.RED, 4))
    flag.add_stack(PLAYER_A, CardGenerator.tactic(TacticMorales.LEADER_ALEXANDER))
    flag.add_stack(PLAYER_B, CardGenerator.troop(TroopColors.BLUE, 2))
    flag.add_stack(PLAYER_B, CardGenerator.troop(TroopColors.BLUE, 3))
    flag.add_stack(PLAYER_B, CardGenerator.troop(TroopColors.BLUE, 4))
    assert _check_resolve(flag, state) == PLAYER_A


def test_solve_superwild_wedge_vs_wedge():  # noqa: D103
    state = GameState.new()
    flag: Flag = state.get_flags()[0]
    flag.add_stack(PLAYER_A, CardGenerator.troop(TroopColors.RED, 9))
    flag.add_stack(PLAYER_A, CardGenerator.tactic(TacticMorales.COMPANION_CAVALRY))
    flag.add_stack(PLAYER_A, CardGenerator.tactic(TacticMorales.LEADER_ALEXANDER))
    flag.add_stack(PLAYER_B, CardGenerator.troop(TroopColors.BLUE, 2))
    flag.add_stack(PLAYER_B, CardGenerator.troop(TroopColors.BLUE, 3))
    flag.add_stack(PLAYER_B, CardGenerator.troop(TroopColors.BLUE, 4))
    assert _check_resolve(flag, state) == PLAYER_A


def test_solve_same_wedge():  # noqa: D103
    state = GameState.new()
    flag: Flag = state.get_flags()[0]
    flag.add_stack(PLAYER_A, CardGenerator.troop(TroopColors.RED, 3))
    flag.add_stack(PLAYER_A, CardGenerator.troop(TroopColors.RED, 4))
    flag.add_stack(PLAYER_A, CardGenerator.troop(TroopColors.RED, 2))
    flag.add_stack(PLAYER_B, CardGenerator.troop(TroopColors.BLUE, 2))
    flag.add_stack(PLAYER_B, CardGenerator.troop(TroopColors.BLUE, 3))
    flag.add_stack(PLAYER_B, CardGenerator.troop(TroopColors.BLUE, 4))
    assert _check_resolve(flag, state) == PLAYER_A


def test_solve_same_wedge_reversed():  # noqa: D103
    state = GameState.new()
    flag: Flag = state.get_flags()[0]
    flag.add_stack(PLAYER_B, CardGenerator.troop(TroopColors.BLUE, 2))
    flag.add_stack(PLAYER_B, CardGenerator.troop(TroopColors.BLUE, 3))
    flag.add_stack(PLAYER_B, CardGenerator.troop(TroopColors.BLUE, 4))
    flag.add_stack(PLAYER_A, CardGenerator.troop(TroopColors.RED, 3))
    flag.add_stack(PLAYER_A, CardGenerator.troop(TroopColors.RED, 4))
    flag.add_stack(PLAYER_A, CardGenerator.troop(TroopColors.RED, 2))
    assert _check_resolve(flag, state) == PLAYER_B


def test_solve_wild_wedge_vs_phalanx():  # noqa: D103
    state = GameState.new()
    flag: Flag = state.get_flags()[0]
    flag.add_stack(PLAYER_A, CardGenerator.troop(TroopColors.RED, 3))
    flag.add_stack(PLAYER_A, CardGenerator.troop(TroopColors.RED, 4))
    flag.add_stack(PLAYER_A, CardGenerator.tactic(TacticMorales.LEADER_ALEXANDER))
    flag.add_stack(PLAYER_B, CardGenerator.troop(TroopColors.BLUE, 8))
    flag.add_stack(PLAYER_B, CardGenerator.troop(TroopColors.GREEN, 8))
    flag.add_stack(PLAYER_B, CardGenerator.troop(TroopColors.YELLOW, 8))
    assert _check_resolve(flag, state) == PLAYER_A


def test_solve_failed_wedge_but_battalion_vs_battalion():  # noqa: D103
    state = GameState.new()
    flag: Flag = state.get_flags()[0]
    flag.add_stack(PLAYER_A, CardGenerator.troop(TroopColors.RED, 3))
    flag.add_stack(PLAYER_A, CardGenerator.troop(TroopColors.RED, 4))
    flag.add_stack(PLAYER_A, CardGenerator.troop(TroopColors.RED, 7))
    flag.add_stack(PLAYER_B, CardGenerator.troop(TroopColors.BLUE, 1))
    flag.add_stack(PLAYER_B, CardGenerator.troop(TroopColors.BLUE, 3))
    flag.add_stack(PLAYER_B, CardGenerator.troop(TroopColors.BLUE, 6))
    assert _check_resolve(flag, state) == PLAYER_A


def _check_resolve(flag: Flag, state: GameState) -> int:
    used_cards = aggregate_used_troops(state)
    return check_resolvable_for_single_flag(flag, used_cards)

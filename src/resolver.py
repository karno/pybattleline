"""Battle Line Flags Resolver Engine."""

import itertools
from itertools import chain
from typing import Collection, Iterable, List, Optional, Tuple
from src.cards import (
    TacticEnvironmentCard,
    TacticMoraleCard,
    TroopAndTacticMoraleCard,
    TroopCard,
)
from src.cardtypes import Formations, TacticMorales, Tactics, TroopColors
from src.game import Flag, GameState, PLAYER_A, PLAYER_B, PLAYER_UNRESOLVED


def check_resolve(flag: Flag, state: GameState) -> int:
    # check flag is not resolved yet
    if flag.is_resolved():
        return flag.get_resolved()
    # to resolve a flag acquisition, at least 1 user must be placed
    # 3 troop cards into his position.
    # (if there is Mud card, 4 troop cards are required.)
    envs: Iterable[TacticEnvironmentCard] = itertools.chain.from_iterable(
        [flag.get_stacked_envs(p) for p in range(2)]
    )
    mudness = Tactics.MUD in list([e.get_tactics() for e in envs])
    required_card_num = 4 if mudness else 3
    fullfilled = [False, False]
    for player in range(2):
        if len(flag.get_stacked_cards(player)) >= required_card_num:
            fullfilled[player] = True
    if not any(fullfilled):
        # anyone not satisfied
        return PLAYER_UNRESOLVED
    if all(fullfilled):
        comp = _compare_formations(
            flag.get_stacked_cards(PLAYER_A), flag.get_stacked_cards(PLAYER_B)
        )
        if comp != PLAYER_UNRESOLVED:
            return comp
        return PLAYER_A if flag.get_last_stacked_player() == PLAYER_B else PLAYER_B
    return PLAYER_A


def _compare_formations(
    stack_a: Collection[TroopAndTacticMoraleCard],
    stack_b: Collection[TroopAndTacticMoraleCard],
) -> int:
    assert len(stack_a) == len(stack_b)
    return PLAYER_UNRESOLVED


def _eligible_for_wedge(stack: Collection[TroopAndTacticMoraleCard]) -> bool:
    return _has_same_colors(stack)[0] and _has_consecutive_values(stack)


def _eligible_for_phalanx(stack: Collection[TroopAndTacticMoraleCard]) -> bool:
    return _has_same_values(stack)[0]


def _eligible_for_battallion(stack: Collection[TroopAndTacticMoraleCard]) -> bool:
    return _has_same_colors(stack)[0]


def _eligible_for_skirmish(stack: Collection[TroopAndTacticMoraleCard]) -> bool:
    return _has_consecutive_values(stack)


def _eligible_for_host(stack: Collection[TroopAndTacticMoraleCard]) -> bool:
    return True


def _has_same_colors(
    stack: Collection[TroopAndTacticMoraleCard],
) -> Tuple[bool, Optional[TroopColors]]:
    card_color: Optional[TroopColors] = None

    # check troop cards
    for c in stack:
        if isinstance(c, TacticMoraleCard):
            # when coming the tactic morales, just skip it
            # (because it is a wildcard)
            pass
        elif isinstance(c, TroopCard):
            if card_color and card_color != c.get_color():
                # color not matched
                return False, None
            card_color = c.get_color()
        else:
            raise ValueError("Invalid card: {}".format(repr(c)))

    # tactic cards have a wild color
    return True, card_color


def _has_same_values(
    stack: Collection[TroopAndTacticMoraleCard],
) -> Tuple[bool, Optional[int]]:
    card_number: Optional[int] = None
    tacticmorales: List[TacticMoraleCard] = []

    # check troop cards
    for c in stack:
        if isinstance(c, TacticMoraleCard):
            # check later
            tacticmorales.append(c)
        elif isinstance(c, TroopCard):
            number = int(c.get_troop())
            if card_number and card_number != number:
                # number not matched
                return False, None
            card_number = number
        else:
            raise ValueError("Invalid card: {}".format(repr(c)))

    # check tactic cards
    tactic_types = list([t.get_tactics() for t in tacticmorales])
    # check wild 8
    if TacticMorales.COMPANION_CAVALRY in tactic_types:
        # must be 8
        if card_number and card_number != 8:
            return False, None
        card_number = 8
    if TacticMorales.SHIELD_BEARERS in tactic_types:
        if card_number and card_number >= 4:
            return False, None

    # leader cards can be accepted by any number
    return True, card_number


def _has_consecutive_values(
    stack: Collection[TroopAndTacticMoraleCard], skippable: int = 0
) -> bool:
    # sorted stack
    card_numbers: List[int] = []
    tacticmorales: List[TacticMoraleCard] = []

    # check troop cards
    for c in stack:
        if isinstance(c, TacticMoraleCard):
            tacticmorales.append(c)
        elif isinstance(c, TroopCard):
            card_numbers.append(int(c.get_troop()))
        else:
            raise ValueError("Invalid card: {}".format(repr(c)))

    # check tactic cards
    tactic_types = list([t.get_tactics() for t in tacticmorales])
    # check wild 8
    if TacticMorales.COMPANION_CAVALRY in tactic_types:
        card_numbers.append(8)
    # wild 1-3
    if TacticMorales.SHIELD_BEARERS in tactic_types:
        for i in reversed(range(1, 4)):
            if i not in card_numbers:
                card_numbers.append(i)
    # wildcard
    if (
        TacticMorales.LEADER_ALEXANDER in tactic_types
        or TacticMorales.LEADER_DARIUS in tactic_types
    ):
        skippable += 1
    return _check_consecutive(card_numbers, skippable)


def _check_consecutive(items: List[int], skippables: int) -> bool:
    items.sort()
    last_num: Optional[int] = None
    for elem in items:
        if not last_num or (last_num + 1) == elem:
            last_num = elem
        else:
            skippables -= 1
            if skippables < 0:
                return False
            last_num += 1
    return True


def find_candidates(
    flag: Flag, player: int, state: GameState
) -> Iterable[Tuple[Formations, Collection[TroopCard]]]:
    pass


# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---


def resolve(state: GameState):
    pass


def aggregate_used_troops(state: GameState) -> List[TroopCard]:
    cards: List[TroopCard] = []
    # aggregate from all flags
    for flag in state.get_flags():
        stacks = chain.from_iterable(
            [flag.get_stacked_cards(PLAYER_A), flag.get_stacked_cards(PLAYER_B)]
        )
        cards.extend([c for c in stacks if isinstance(c, TroopCard)])
    # ... and discarded cards
    ops = chain.from_iterable(
        [state.get_operations(PLAYER_A), state.get_operations(PLAYER_B)]
    )
    discards = [t for t in [op.get_discarded_troop_card() for op in ops] if t]
    cards.extend(discards)
    return cards


def check_resolvable_for_single_flag(
    flag: Flag, used_cards: Collection[TroopCard]
) -> int:
    pass


def possible_maximum_strength_for_wedge(
    stacked_cards: Collection[TroopAndTacticMoraleCard],
    n_cards: int,
    used_cards: Collection[TroopCard],
) -> Tuple[int, bool]:
    """Cards have the same color and consecutive values."""
    have_same_color, color = _has_same_colors(stacked_cards)
    if not have_same_color:  # have different colors
        return 0, False
    strength, result, cand_tuples = _get_candidate_consecutive_tuples(
        stacked_cards, n_cards
    )
    if strength:  # strength is fixed
        return strength, result
    for c in used_cards:
        if c.get_color() != color:
            # not related
            continue
        value = int(c.get_troop())
        cand_tuples = [(v, c) for v, c in cand_tuples if value not in c]
    if len(cand_tuples) == 0:
        return 0, False
    return max([v for v, _ in cand_tuples]), False


def possible_maximum_strength_for_phalanx(
    stacked_cards: Collection[TroopAndTacticMoraleCard],
    n_cards: int,
    used_cards: Collection[TroopCard],
) -> Tuple[int, bool]:
    """Cards have the same value."""
    number: Optional[int] = None
    is_shield = False
    for c in stacked_cards:
        if isinstance(c, TroopCard):
            value = int(c.get_troop())
            if number and number != value:
                return 0, False
            number = value
            continue
        if isinstance(c, TacticMoraleCard):
            morale = c.get_tactic_morales()
            if morale in (TacticMorales.LEADER_ALEXANDER, TacticMorales.LEADER_DARIUS):
                # wildcard
                continue
            if morale == TacticMorales.COMPANION_CAVALRY:
                # anycolor of 8
                if number and number != 8:
                    return 0, False
                number = 8
                continue
            if morale == TacticMorales.SHIELD_BEARERS:
                # evaluate later
                is_shield = True
                continue
        raise ValueError("invalid card: {}".format(c))
    required = n_cards - len(stacked_cards)
    if required == 0:
        assert number is not None
        return number * n_cards, True
    # find candidates
    candidates = reversed(
        sorted(
            [number]
            if number
            else list(range(1, 4))
            if is_shield
            else list(range(1, 11))
        )
    )
    for n in candidates:
        remain = 6
        # check used cards
        for c in used_cards:
            if c.get_troop() == n:
                remain -= 1
        # if remained card is less than used
        if remain > required:
            return n * n_cards, False
    return 0, False


def possible_maximum_strength_for_battalion(
    stacked_cards: Collection[TroopAndTacticMoraleCard],
    n_cards: int,
    used_cards: Collection[TroopCard],
) -> Tuple[int, bool]:
    """Cards have the same color."""
    # check all cards have the same colors
    have_same_color, color = _has_same_colors(stacked_cards)
    if not have_same_color:
        # not eligible for batalion
        return 0, False
    required = n_cards - len(stacked_cards)
    cur_value = _calculate_current_maximum_power(stacked_cards)
    if required == 0:
        return cur_value, True
    colors = [color] if color is not None else list(TroopColors)

    strength_combination = [
        _calculate_max_combination(required, c, used_cards) for c in colors
    ]
    return (max(strength_combination) + cur_value), False


def possible_maximum_strength_for_skirmish(
    stacked_cards: Collection[TroopAndTacticMoraleCard],
    n_cards: int,
    used_cards: Collection[TroopCard],
) -> Tuple[int, bool]:
    """Cards have the consecutive values(with any colors)."""
    strength, result, cand_tuples = _get_candidate_consecutive_tuples(
        stacked_cards, n_cards
    )
    if strength:  # strength is fixed
        return strength, result
    # check volatiled numbers
    volatility = [6] * 10
    for c in used_cards:
        value = int(c.get_troop())
        # value is between 1~10 -> 0~9
        volatility[value - 1] -= 1
    # remove volatiled number from candidates
    for i, remain in enumerate(volatility):
        if remain > 0:
            continue
        value = i + 1
        cand_tuples = [(v, c) for v, c in cand_tuples if value not in c]
    if len(cand_tuples) == 0:
        return 0, False
    return max([v for v, _ in cand_tuples]), False


def possible_maximum_strength_for_host(
    stacked_cards: Collection[TroopAndTacticMoraleCard],
    n_cards: int,
    used_cards: Collection[TroopCard],
) -> Tuple[int, bool]:
    """Cards are not any other formations."""
    required = n_cards - len(stacked_cards)
    cur_value = _calculate_current_maximum_power(stacked_cards)
    if required == 0:
        return cur_value, True
    return (_calculate_max_combination(required, None, used_cards) + cur_value), False


def _get_candidate_consecutive_tuples(
    stacked_cards: Collection[TroopAndTacticMoraleCard], n_cards: int
) -> Tuple[Optional[int], bool, List[Tuple[int, List[int]]]]:
    """Check cards have the consecutive values.
    
    Returns:
        Optional[int] - when the formation is completed, 
            (or confirmed the formation will not completed)
            represents the strength of formation
        bool - whether the formation is completed 
        List[Tuple[int, List[int]]] - list of candidates
    """
    # get the candidates
    cand_iter = _iterate_consecutive_candidates_number(n_cards)
    # bind with strength of formation
    cand_tuples = [(sum(c), c) for c in cand_iter]
    # filter candidates by stacked cards
    for card in stacked_cards:
        cand_tuples = _filter_candidate_lists_by_card(card, cand_tuples)
        # check candidates are remaining
        if len(cand_tuples) == 0:
            return 0, False, []
    # check completion for search
    resolved_cand_values = [v for v, c in cand_tuples if len(c) == 0]
    if len(resolved_cand_values) > 0:
        assert len(stacked_cards) == n_cards
        return max(resolved_cand_values), True, cand_tuples
    assert (
        len(stacked_cards) < n_cards
    ), "failed to resolve, stack size: {}, required: {}".format(
        len(stacked_cards), n_cards
    )
    return None, False, cand_tuples


def _filter_candidate_lists_by_card(
    card: TroopAndTacticMoraleCard, cand_tuples: List[Tuple[int, List[int]]]
) -> List[Tuple[int, List[int]]]:
    result_list: List[Tuple[int, List[int]]] = []
    for cand_tuple in cand_tuples:
        result_list.extend(_check_candidate_list_by_card(card, cand_tuple))
    return result_list


def _check_candidate_list_by_card(
    card: TroopAndTacticMoraleCard, cand_tuple: Tuple[int, List[int]]
) -> List[Tuple[int, List[int]]]:
    if isinstance(card, TroopCard):
        return _check_candidate_list_by_troop(card.get_troop(), cand_tuple)
    if isinstance(card, TacticMoraleCard):
        value = card.get_tactic_morales()
        if value in (TacticMorales.LEADER_ALEXANDER, TacticMorales.LEADER_DARIUS):
            # wildcard instantiates the new candidates
            # [4, 5, 6] => [[4, 5], [5, 6], [4, 6]]
            # [6, 7] => [[6], [7]]
            cs = itertools.combinations(cand_tuple[1], len(cand_tuple[1]) - 1)
            return [(cand_tuple[0], list(c)) for c in cs]
        if value == TacticMorales.COMPANION_CAVALRY:
            # wild 8
            return _check_candidate_list_by_troop(8, cand_tuple)
        if value == TacticMorales.SHIELD_BEARERS:
            return list(
                itertools.chain.from_iterable(
                    [
                        _check_candidate_list_by_troop(
                            i,
                            # create copy of cand_tuple
                            (cand_tuple[0], cand_tuple[1][:]),
                        )
                        for i in range(1, 4)  # iterate over 1 to 3
                    ]
                )
            )
    raise ValueError("invalid cardtype found in stack.")


def _check_candidate_list_by_troop(
    value: int, cand_tuple: Tuple[int, List[int]]
) -> List[Tuple[int, List[int]]]:
    if value not in cand_tuple[1]:
        # not satisfied
        return []
    # delete item from collection
    cand_tuple[1].remove(value)
    return [cand_tuple]


def _calculate_max_combination(
    n_req_cards: int, color: Optional[TroopColors], used_cards: Collection[TroopCard]
) -> int:
    cards = ([1] if color is not None else [6]) * 10  # 1~10
    for c in used_cards:
        if color is not None and c.get_color() != color:
            continue
        cards[int(c.get_troop()) - 1] -= 1
    value = 0
    for i in reversed(range(10)):
        if cards[i] > 0:
            value += i + 1
            n_req_cards -= 1
        if n_req_cards == 0:
            return value
    # requirement not satisfied
    assert n_req_cards > 0
    return 0


def _calculate_current_maximum_power(
    stacked_cards: Collection[TroopAndTacticMoraleCard],
) -> int:
    value = 0
    for c in stacked_cards:
        if isinstance(c, TroopCard):
            value += int(c.get_troop())
        elif isinstance(c, TacticMoraleCard):
            morale = c.get_tactic_morales()
            if morale in (TacticMorales.LEADER_ALEXANDER, TacticMorales.LEADER_DARIUS):
                value += 10
            elif morale == TacticMorales.COMPANION_CAVALRY:
                value += 8
            elif morale == TacticMorales.SHIELD_BEARERS:
                value += 3
            else:
                raise ValueError("Unknown tactic morales: {}".format(morale))
        else:
            raise ValueError("Unknown card: {}".format(c))
    return value


def _iterate_consecutive_candidates_number(n_cards: int) -> Iterable[List[int]]:
    for i in reversed(range(1, 11 - n_cards)):
        yield list(range(i, n_cards))

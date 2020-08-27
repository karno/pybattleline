"""Battle Line Flags Resolver Engine."""

import itertools
from itertools import chain
from typing import Collection, Iterable, List, Optional, Tuple
from src.cards import (
    TacticMoraleCard,
    TroopAndTacticMoraleCard,
    TroopCard,
)
from src.cardtypes import TacticMorales, TroopColors
from src.game import Flag, GameState, PLAYER_A, PLAYER_B, PLAYER_UNRESOLVED


def resolve(state: GameState):
    used_cards = aggregate_used_troops(state)
    for flag in state.get_flags():
        if flag.is_resolved():
            # already resolved
            continue
        resolve = check_resolvable_for_single_flag(flag, used_cards)
        # resolve flag
        if resolve != PLAYER_UNRESOLVED:
            flag.resolve(resolve)


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
    n_cards = flag.get_required_card_num()
    resolver_funcs = [
        possible_maximum_strength_for_wedge,
        possible_maximum_strength_for_phalanx,
        possible_maximum_strength_for_battalion,
        possible_maximum_strength_for_skirmish,
        possible_maximum_strength_for_host,
    ]
    if flag.is_formation_disabled():
        # all formation is disabled and only hosts available
        resolver_funcs = [possible_maximum_strength_for_host]
    for resolver in resolver_funcs:
        a_cards = flag.get_stacked_cards(PLAYER_A)
        b_cards = flag.get_stacked_cards(PLAYER_B)
        a_strength, a_resolvable = resolver(a_cards, n_cards, used_cards)
        b_strength, b_resolvable = resolver(b_cards, n_cards, used_cards)
        if a_resolvable and b_resolvable and a_strength == b_strength:
            # faster user wins
            return PLAYER_A if flag.get_last_stacked_player() == PLAYER_B else PLAYER_B
        if a_resolvable:
            if a_strength > b_strength:
                return PLAYER_A
        if b_resolvable:
            if b_strength > a_strength:
                return PLAYER_B
        if a_strength > 0 or b_strength > 0:
            # could not be resolved yet
            return PLAYER_UNRESOLVED
        # could not build the formation, continue to weaker formation type...
    # not resolved
    return PLAYER_UNRESOLVED


def possible_maximum_strength_for_wedge(
    stacked_cards: Collection[TroopAndTacticMoraleCard],
    n_cards: int,
    used_cards: Collection[TroopCard],
) -> Tuple[int, bool]:
    """Cards have the same color and consecutive values."""
    have_same_color, color = _check_same_color_in_stack(stacked_cards)
    if not have_same_color:  # have different colors
        return 0, False
    strength, result, cand_tuples = _check_consecutive_formation(stacked_cards, n_cards)
    if strength is not None:  # strength is fixed
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
            if number is not None and number != value:
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
                if number is not None and number != 8:
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
            if number is not None
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
    have_same_color, color = _check_same_color_in_stack(stacked_cards)
    if not have_same_color:
        # not eligible for batalion
        return 0, False
    required = n_cards - len(stacked_cards)
    cur_value = _calculate_strength_of_stack(stacked_cards)
    if required == 0:
        return cur_value, True
    colors = [color] if color is not None else list(TroopColors)

    strength_combination = [
        _calculate_maximum_available_strength(required, c, used_cards) or 0
        for c in colors
    ]
    max_str_com = max(strength_combination)
    if max_str_com == 0:
        return 0, False
    return max_str_com + cur_value, False


def possible_maximum_strength_for_skirmish(
    stacked_cards: Collection[TroopAndTacticMoraleCard],
    n_cards: int,
    used_cards: Collection[TroopCard],
) -> Tuple[int, bool]:
    """Cards have the consecutive values(with any colors)."""
    strength, result, cand_tuples = _check_consecutive_formation(stacked_cards, n_cards)
    if strength is not None:  # strength is fixed
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
    cur_value = _calculate_strength_of_stack(stacked_cards)
    if required == 0:
        return cur_value, True
    max_str_com = _calculate_maximum_available_strength(required, None, used_cards) or 0
    if max_str_com == 0:
        return 0, False
    return max_str_com + cur_value, False


def _check_consecutive_formation(
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
        result_list.extend(_check_candidate_tuple_by_card(card, cand_tuple))
    return result_list


def _check_candidate_tuple_by_card(
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


def _calculate_maximum_available_strength(
    n_req_cards: int, color: Optional[TroopColors], used_cards: Collection[TroopCard]
) -> Optional[int]:
    assert n_req_cards > 0
    cards = ([1] if color is not None else [6]) * 10  # 1~10
    for c in used_cards:
        if color is not None and c.get_color() != color:
            continue
        cards[int(c.get_troop()) - 1] -= 1
    value = 0
    for i in reversed(range(10)):
        while cards[i] > 0 and n_req_cards > 0:
            value += i + 1
            cards[i] -= 1
            n_req_cards -= 1
        if n_req_cards == 0:
            return value
    # requirement not satisfied
    assert n_req_cards > 0
    return None


def _calculate_strength_of_stack(
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


def _check_same_color_in_stack(
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


def _iterate_consecutive_candidates_number(n_cards: int) -> Iterable[List[int]]:
    for i in reversed(range(1, 12 - n_cards)):
        yield list(range(i, i + n_cards))

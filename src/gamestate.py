"""Battle Line Game System."""

import copy
from copy import deepcopy
from typing import Iterable, List, Optional, Sequence

from src.cards.cards import Card, TacticGuileCard, TroopAndTacticMoraleCard
from src.cards.decks import TacticsDeck, TroopsDeck
from src.consts import (
    NUM_INITIAL_HAND,
    PLAYER_A,
    PLAYER_B,
    PLAYER_IDS,
    PLAYER_UNRESOLVED,
)
from src.flag import Flag


class GuileOperation:
    """Represent the operated tactics card and discarded troops card if existing."""

    def __init__(
        self,
        guile_card: TacticGuileCard,
        discarded_card: Optional[TroopAndTacticMoraleCard],
    ) -> None:
        self._guile_card = guile_card
        self._discarded = discarded_card

    def get_tactic_guile_card(self) -> TacticGuileCard:
        return self._guile_card

    def get_discarded_troop_card(self) -> Optional[TroopAndTacticMoraleCard]:
        return self._discarded

    def __repr__(self) -> str:
        text = repr(self._guile_card)
        if self._discarded:
            text += " | " + repr(self._guile_card)
        return text


class GameState:
    @staticmethod
    def new() -> "GameState":
        troops = TroopsDeck.shuffled()
        a_list: List[Card] = list(
            sorted([troops.draw() for _ in range(NUM_INITIAL_HAND)])
        )
        b_list: List[Card] = list(
            sorted([troops.draw() for _ in range(NUM_INITIAL_HAND)])
        )
        return GameState(
            troops,
            TacticsDeck.shuffled(),
            [Flag() for _ in range(9)],
            [[], []],
            [a_list, b_list],
        )

    def __init__(
        self,
        troops_deck: TroopsDeck,
        tactics_deck: TacticsDeck,
        flags: Iterable[Flag],
        operations: Iterable[List[GuileOperation]],
        hands: Iterable[List[Card]],
    ) -> None:
        self._troops_deck = troops_deck
        self._tactics_deck = tactics_deck
        self._flags = list(flags)
        self._operations = list(operations)
        self._hands = list(hands)
        assert len(self._flags) == 9
        assert len(self._operations) == 2
        assert len(self._hands) == 2

    def clone(self) -> "GameState":
        return deepcopy(self)

    def get_troops_deck(self) -> TroopsDeck:
        return self._troops_deck

    def get_tactics_deck(self) -> TacticsDeck:
        return self._tactics_deck

    def get_flags(self) -> Sequence[Flag]:
        return self._flags

    def contain_flag(self, flag: Flag) -> bool:
        for f in self._flags:
            if f is flag:
                return True
        return False

    def get_local_flag(self, other: "GameState", other_flag: Flag) -> Flag:
        if other is self or self.contain_flag(other_flag):
            return other_flag
        for i, flag in enumerate(other.get_flags()):
            if flag is other_flag:
                return self._flags[i]
        raise ValueError("Unknown flag")

    def get_hands(self, player: int) -> List[Card]:
        return self._hands[player]

    def add_hand(self, player: int, card: Card) -> None:
        self._hands[player].append(card)
        self._hands[player].sort()

    def contain_hands(self, hands: List[Card]) -> bool:
        for c in self._hands:
            if c is hands:
                return True
        return False

    def get_operations(self, player: int) -> List[GuileOperation]:
        return self._operations[player]

    def contain_operations(self, operation: GuileOperation) -> bool:
        for ops in self._operations:
            for op in ops:
                if op is operation:
                    return True
        return False

    def __deepcopy__(self, memo) -> "GameState":
        return GameState(
            copy.deepcopy(self._troops_deck, memo),
            copy.deepcopy(self._tactics_deck, memo),
            copy.deepcopy(self._flags, memo),
            copy.deepcopy(self._operations, memo),
            copy.deepcopy(self._hands, memo),
        )

    def get_winner(self) -> int:
        obtained_flags = [0 for _ in PLAYER_IDS]
        continuously_obtained_flags = [0 for _ in PLAYER_IDS]
        for flag in self._flags:
            state = flag.get_resolved()
            if state == PLAYER_UNRESOLVED:
                # flag is in play (not obtained)
                continuously_obtained_flags = [0 for _ in PLAYER_IDS]
            else:
                continuously_obtained_flags[state] += 1
                obtained_flags[state] += 1
            for p in PLAYER_IDS:
                if continuously_obtained_flags[p] >= 3 or obtained_flags[p] >= 5:
                    # player p is winner!
                    return p
        # game in play
        return PLAYER_UNRESOLVED

    def __repr__(self) -> str:
        text = ""
        # player b operations (in reverse)
        for op in reversed(self._operations[PLAYER_B]):
            text += repr(op)
        # flags
        text += Flag.repr_flags(self._flags)
        # player a operations
        for op in self._operations[PLAYER_A]:
            text += repr(op)
        return text

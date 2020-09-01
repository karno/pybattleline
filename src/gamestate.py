"""Battle Line Game System."""

import copy
from typing import Iterable, List, Optional, Sequence

from src.cards.cards import TacticGuileCard, TroopCard
from src.cards.decks import TacticsDeck, TroopsDeck
from src.consts import PLAYER_A, PLAYER_B, PLAYER_UNRESOLVED
from src.flag import Flag


class GuileOperation:
    """Represent the operated tactics card and discarded troops card if existing."""

    def __init__(
        self, guile_card: TacticGuileCard, discarded_troop: Optional[TroopCard]
    ) -> None:
        self._guile_card = guile_card
        self._discarded = discarded_troop

    def get_guile_card(self) -> TacticGuileCard:
        return self._guile_card

    def get_discarded_troop_card(self) -> Optional[TroopCard]:
        return self._discarded

    def __repr__(self) -> str:
        text = repr(self._guile_card)
        if self._discarded:
            text += " | " + repr(self._guile_card)
        return text


class GameState:
    @staticmethod
    def new() -> "GameState":
        return GameState(
            TroopsDeck.shuffled(),
            TacticsDeck.shuffled(),
            [Flag() for _ in range(9)],
            [[], []],
        )

    def __init__(
        self,
        troops_deck: TroopsDeck,
        tactics_deck: TacticsDeck,
        flags: Iterable[Flag],
        operations: List[List[GuileOperation]],
    ) -> None:
        self._troops_deck = troops_deck
        self._tactics_deck = tactics_deck
        self._flags = list(flags)
        self._operations = operations
        assert len(self._operations) == 2

    def get_troops_deck(self) -> TroopsDeck:
        return self._troops_deck

    def get_tactics_deck(self) -> TacticsDeck:
        return self._tactics_deck

    def get_flags(self) -> Sequence[Flag]:
        return self._flags

    def get_operations(self, player: int) -> List[GuileOperation]:
        return self._operations[player]

    def __deepcopy__(self, memo) -> "GameState":
        return GameState(
            copy.deepcopy(self._troops_deck, memo),
            copy.deepcopy(self._tactics_deck, memo),
            copy.deepcopy(self._flags, memo),
            copy.deepcopy(self._operations, memo),
        )

    def get_winner(self) -> int:
        obtained_flags = [0] * 2
        continuously_obtained_flags = [0] * 2
        for flag in self._flags:
            state = flag.get_resolved()
            if state == PLAYER_UNRESOLVED:
                # flag is in play (not obtained)
                continuously_obtained_flags = [0] * 2
            else:
                continuously_obtained_flags[state] += 1
                obtained_flags[state] += 1
            for p in range(0, 2):
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

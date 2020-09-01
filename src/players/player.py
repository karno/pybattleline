"""Game player definition."""

from typing import Iterable

from src.cards.cards import Card, TacticGuileCard
from src.consts import PLAYER_UNRESOLVED
from src.flag import Flag
from src.gamestate import GameState


class Player:
    def __init__(self, player_id: int, hands: Iterable[Card]) -> None:
        self._id = player_id
        self._hands = list(hands)
        assert len(self._hands) == 7, "hands must be 7 cards."

    def play(self, game: GameState) -> GameState:
        pass

    def _get_user_repr(self) -> str:
        return "PLAYER_A" if self._id == PLAYER_UNRESOLVED else "PLAYER_B"

    def _can_play_troop_tactic_morales_for_flag(self, flag: Flag) -> bool:
        stacked = flag.get_stacked_cards(self._id)
        return len(stacked) < flag.get_required_card_num()

    def _can_play_tactic_envs_for_flag(self, flag: Flag) -> bool:
        return flag.get_resolved() != PLAYER_UNRESOLVED

    def _can_play_tactic_guiles(self, card: TacticGuileCard) -> bool:
        pass

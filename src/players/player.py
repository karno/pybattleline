"""Game player definition."""

from abc import ABCMeta, abstractmethod
from typing import List, Optional, Tuple

from src.cards.cards import (
    Card,
    TacticCard,
    TacticEnvironmentCard,
    TacticGuileCard,
    TacticMoraleCard,
    TroopAndTacticMoraleCard,
    TroopCard,
)
from src.cards.cardtypes import TacticGuiles, TacticMorales
from src.consts import PLAYER_A, PLAYER_B, PLAYER_IDS, PLAYER_UNRESOLVED
from src.flag import Flag
from src.gamestate import GameState, GuileOperation


class Player(metaclass=ABCMeta):
    def __init__(self, player_id: int) -> None:
        self._id = player_id
        assert self._id in PLAYER_IDS

    @abstractmethod
    def play(self, state: GameState) -> GameState:
        raise NotImplementedError()

    def get_id(self) -> int:
        return self._id

    def get_opposite_id(self) -> int:
        return PLAYER_A if self._id == PLAYER_A else PLAYER_B

    def get_hands(self, state: GameState) -> List[Card]:
        return state.get_hands(self._id)

    def _get_user_repr(self) -> str:
        return "Player A" if self._id == PLAYER_A else "Player B"

    def _can_play_troop_tactic_morales_for_flag(self, flag: Flag) -> bool:
        stacked = flag.get_stacked_cards(self._id)
        return len(stacked) < flag.get_required_card_num()

    def _can_play_tactic_envs_for_flag(self, flag: Flag) -> bool:
        return flag.get_resolved() == PLAYER_UNRESOLVED

    def _can_play_tactics(self, card: TacticCard, state: GameState) -> bool:
        deployed_tactics: List[List[TacticCard]] = [[], []]
        # calculate sum of deployed tactics
        for p in PLAYER_IDS:
            for f in state.get_flags():
                troops = f.get_stacked_cards(p)
                deployed_tactics[p].extend(
                    [c for c in troops if isinstance(c, TacticCard)]
                )
                deployed_tactics[p].extend(f.get_stacked_envs(p))
            deployed_tactics[p].extend(
                [o.get_tactic_guile_card() for o in state.get_operations(p)]
            )
        deployable_cards_num = len(deployed_tactics[self.get_opposite_id()]) + 1
        leaders = [
            TacticMorales.LEADER_ALEXANDER,
            TacticMorales.LEADER_DARIUS,
        ]
        if isinstance(card, TacticMoraleCard) and card.get_tactic_morales() in leaders:
            for deployed_card in deployed_tactics[self.get_id()]:
                if (
                    isinstance(deployed_card, TacticMoraleCard)
                    and deployed_card.get_tactic_morales() in leaders
                ):
                    # you can't play both of leader cards
                    return False
        return len(deployed_tactics[self.get_id()]) <= deployable_cards_num

    def _play_troop_tactic_morales_for_flag(
        self, state: GameState, flag: Flag, card: TroopAndTacticMoraleCard
    ) -> GameState:
        state, flag = self._generate_new_state(state, flag)
        hands = self.get_hands(state)
        assert card in hands
        assert self._can_play_troop_tactic_morales_for_flag(flag)
        hands.remove(card)  # type: ignore
        flag.add_stack(self._id, card)
        return state

    def _play_tactic_envs_for_flag(
        self, state: GameState, flag: Flag, card: TacticEnvironmentCard
    ) -> GameState:
        state, flag = self._generate_new_state(state, flag)
        hands = self.get_hands(state)
        assert card in hands
        assert self._can_play_tactic_envs_for_flag(flag)
        hands.remove(card)
        flag.add_env(self._id, card)
        return state

    def _play_tactic_guile_scout(
        self,
        state: GameState,
        card: TacticGuileCard,
        draw_size_troops_and_tactics_deck: Tuple[int, int],
        ret_card: Tuple[Card, Card],
    ) -> GameState:
        assert card.get_tactic_guiles() == TacticGuiles.SCOUT
        state = state.clone()
        draw_troops, draw_tactics = draw_size_troops_and_tactics_deck
        troops = [state.get_troops_deck().draw() for _ in range(draw_troops)]
        tactics = [state.get_tactics_deck().draw() for _ in range(draw_tactics)]
        hands = state.get_hands(self.get_id())
        hands.extend(troops)
        hands.extend(tactics)
        for c in ret_card:
            assert c in hands
            if isinstance(c, TroopCard):
                state.get_troops_deck().back(c)
            elif isinstance(c, TacticCard):
                state.get_tactics_deck().back(c)
            else:
                raise ValueError(f"Unknown card type: {repr(card)}")
        hands.sort()
        state.get_operations(self.get_id()).append(GuileOperation(card, None))
        return state

    def _play_redeploy_for_flag(
        self,
        state: GameState,
        card: TacticGuileCard,
        reclaiming_flag: Flag,
        reclaimed_card: TroopAndTacticMoraleCard,
        redeploy_flag: Optional[Flag],
    ) -> GameState:
        assert card.get_tactic_guiles() == TacticGuiles.REDEPLOY
        self._play_tactic_guile_reclaims(
            state, card, reclaiming_flag, reclaimed_card, self.get_id(), redeploy_flag
        )

    def _play_deserter_for_flag(
        self,
        state: GameState,
        card: TacticGuileCard,
        reclaiming_flag: Flag,
        reclaimed_card: TroopAndTacticMoraleCard,
    ) -> GameState:
        self._play_tactic_guile_reclaims(
            state, card, reclaiming_flag, reclaimed_card, self.get_opposite_id(), None
        )

    def _play_traitor_for_flag(
        self,
        state: GameState,
        card: TacticGuileCard,
        reclaiming_flag: Flag,
        reclaimed_card: TroopAndTacticMoraleCard,
        redeploy_flag: Flag,
    ) -> GameState:
        assert card.get_tactic_guiles() == TacticGuiles.TRAITOR
        return self._play_tactic_guile_reclaims(
            state,
            card,
            reclaiming_flag,
            reclaimed_card,
            self.get_opposite_id(),
            redeploy_flag,
        )

    def _play_tactic_guile_reclaims(
        self,
        state: GameState,
        card: TacticGuileCard,
        reclaiming_flag: Flag,
        reclaimed_card: TroopAndTacticMoraleCard,
        reclaimed_player: int,
        redeploy_flag: Optional[Flag],
    ) -> GameState:
        assert card.get_tactic_guiles() in [
            TacticGuiles.REDEPLOY,
            TacticGuiles.DESERTER,
            TacticGuiles.TRAITOR,
        ]
        new_state, new_reclaiming_flag = self._generate_new_state(
            state, reclaiming_flag
        )
        new_redeploy_flag = (
            new_state.get_local_flag(state, redeploy_flag)
            if redeploy_flag is not None
            else None
        )
        state = new_state
        reclaim_flag = new_reclaiming_flag
        redeploy_flag = new_redeploy_flag
        removal = reclaim_flag.remove_stack(reclaimed_player, reclaimed_card)
        assert removal is not None and reclaimed_card == removal
        if redeploy_flag is not None:
            redeploy_flag.add_stack(self.get_id(), removal)
            state.get_operations(self.get_id()).append(GuileOperation(card, None))
        else:
            state.get_operations(self.get_id()).append(GuileOperation(card, removal))
        return state

    @staticmethod
    def _generate_new_state(state: GameState, flag: Flag) -> Tuple[GameState, Flag]:
        new_state = state.clone()
        new_flag = new_state.get_local_flag(state, flag)
        return new_state, new_flag

"""Player proxy for humans."""

from copy import copy
from typing import Collection, Iterable, List, Optional, Tuple

from src.cards.cards import (
    Card,
    PlayedCard,
    TacticCard,
    TacticEnvironmentCard,
    TacticGuileCard,
    TroopAndTacticMoraleCard,
    TroopCard,
)
from src.cards.cardtypes import TacticGuiles
from src.flag import Flag
from src.gamestate import GameState
from src.players.player import Player


class HumanPlayer(Player):
    def __init__(self, player_id: int) -> None:
        super().__init__(player_id)

    def play(self, state: GameState) -> GameState:
        print(f"{self._get_user_repr()}: TURN START {'-'*60}")
        suppress_draw = False
        while True:
            card = self._choose_hand_to_play(state)
            if card is None:
                # pass
                print(" --> passed.")
                return state
            print(f"You chose: {repr(card)}")
            if isinstance(card, TroopAndTacticMoraleCard):
                flag = self._choose_flag_to_deploy(state, card)
                if flag is None:
                    print(" --> re-select the card")
                    continue
                state = self._play_troop_tactic_morales_for_flag(state, flag, card)
                break
            if isinstance(card, TacticEnvironmentCard):
                flag = self._choose_flag_to_deploy(state, card)
                if flag is None:
                    print(" --> re-select the card")
                    continue
                state = self._play_tactic_envs_for_flag(state, flag, card)
                break
            if isinstance(card, TacticGuileCard):
                new_state = self._play_tactic_guile(state, card)
                if new_state is None:
                    print(" --> re-select the card")
                    continue
                if card.get_tactic_guiles() == TacticGuiles.SCOUT:
                    # card already drew
                    suppress_draw = True
                state = new_state
                break
            raise ValueError(f"Unknown card: {card}")
        if not suppress_draw:
            card = self._draw_deck(state)
            if card is not None:
                state = state.clone()
                state.add_hand(self.get_id(), card)
        print(f"{self._get_user_repr()}: TURN END {'-'*60}")
        return state

    def _choose_hand_to_play(self, state: GameState) -> Optional[Card]:
        hands = self.get_hands(state)
        candidates: List[int] = []
        print("please select the playing card from your hands:")
        for i, c in enumerate(hands):
            if isinstance(c, TacticCard) and not self._can_play_tactics(c, state):
                print(f"[x] -- {repr(c)} : unplayable")
            else:
                print(f"[{i + 1}] -- {repr(c)}")
                candidates.append(i + 1)
        if all([isinstance(c, TacticCard) for c in hands]):
            # could be passed
            print("[0] -- pass your turn")
            candidates.append(0)
        hand_index = await_user_num(candidates)
        return hands[hand_index - 1] if hand_index > 0 else None

    def _choose_flag_to_deploy(
        self, state: GameState, card: PlayedCard, discardable=False
    ) -> Optional[Flag]:
        candidates = [0]
        is_troop = isinstance(card, TroopCard)
        print("please select the flag to deploy:")
        for i, flag in enumerate(state.get_flags()):
            # iterate flags can be placed
            deployable = (
                self._can_play_troop_tactic_morales_for_flag(flag)
                if is_troop
                else self._can_play_tactic_envs_for_flag(flag)
            )
            stacked = flag.get_stacked_cards(self._id)
            opposite = flag.get_opposite_stacked_cards(self._id)
            stacked_envs = flag.get_stacked_envs(self._id)
            opposite_envs = flag.get_opposite_stacked_envs(self._id)
            formatted_line = (
                f"{repr(stacked_envs)} {repr(stacked)}"
                "  vs  "
                f"{repr(opposite)} {repr(opposite_envs)}"
            )
            if deployable:
                print(f"[{i + 1}] -- {formatted_line}")
                candidates.append(i + 1)
            else:
                print(f"[x] -- {formatted_line}")
        if discardable:
            print("[0] -- discard from the game")
        else:
            print("[0] -- return to card selection")
        flag_index = await_user_num(candidates)
        return state.get_flags()[flag_index - 1] if flag_index > 0 else None

    def _play_tactic_guile(
        self, state: GameState, card: TacticGuileCard
    ) -> Optional[GameState]:
        if card.get_tactic_guiles() == TacticGuiles.SCOUT:
            # pick three cards from deck and add to hand, then return
            # two cards from the hand to decks
            return self._play_scout(state, card)
        if card.get_tactic_guiles() == TacticGuiles.REDEPLOY:
            return self._play_redeploy(state, card)
        if card.get_tactic_guiles() == TacticGuiles.DESERTER:
            return self._play_deserter(state, card)
        if card.get_tactic_guiles() == TacticGuiles.TRAITOR:
            return self._play_traitor(state, card)

    def _play_scout(
        self, state: GameState, card: TacticGuileCard
    ) -> Optional[GameState]:
        assert card.get_tactics() == TacticGuiles.SCOUT
        print("choose draw pattern?")
        print("[1] -- draw 3 cards from troops deck")
        print("[2] -- draw 2 cards from troops deck and draw 1 card from tactics deck")
        print("[3] -- draw 1 card from troops deck and draw 2 cards from tactics deck")
        print("[4] -- draw 3 cards from tactics deck")
        print("[0] -- return to select a card")
        user_in = await_user_num(range(5))
        if user_in == 0:
            return None
        # copy to new state
        state = state.clone()
        draw_tactics_num = user_in - 1
        peek_cards: List[Card] = []
        peek_cards.extend(state.get_tactics_deck().peek(draw_tactics_num))
        peek_cards.extend(state.get_troops_deck().peek(3 - draw_tactics_num))
        print("scouted cards: ")
        copy_hands = self.get_hands(state).copy()
        # remove the used card
        copy_hands.remove(card)
        for i, c in enumerate(peek_cards):
            print(f"[{i}]: {repr(c)}")
            copy_hands.append(c)
        # sort my hands
        copy_hands.sort()
        # add to hand
        print("choose 2 cards return to decks:")
        for i, c in enumerate(copy_hands):
            print(f"[{i + 1}]: {repr(c)}")
        input_cand = list(range(1, len(copy_hands) + 1))
        in_1 = await_user_num(input_cand)
        ret_card_1 = copy_hands[in_1 - 1]
        input_cand.remove(in_1)
        in_2 = await_user_num(input_cand)
        ret_card_2 = copy_hands[in_2 - 1]
        return self._play_tactic_guile_scout(
            state,
            card,
            (draw_tactics_num, 3 - draw_tactics_num),
            (ret_card_1, ret_card_2),
        )

    def _play_redeploy(
        self, state: GameState, card: TacticGuileCard
    ) -> Optional[GameState]:
        assert card.get_tactics() == TacticGuiles.REDEPLOY
        flag_and_troop = self._choose_deployed_troops(state, self.get_id())
        if flag_and_troop is None:
            return None
        reclaim_flag, reclaim_card = flag_and_troop
        redeploy_flag = self._choose_flag_to_deploy(state, reclaim_card, True)
        return self._play_redeploy_for_flag(
            state, card, reclaim_flag, reclaim_card, redeploy_flag
        )

    def _play_deserter(
        self, state: GameState, card: TacticGuileCard
    ) -> Optional[GameState]:
        assert card.get_tactics() == TacticGuiles.DESERTER
        flag_and_troop = self._choose_deployed_troops(state, self.get_opposite_id())
        if flag_and_troop is None:
            return None
        reclaim_flag, reclaim_card = flag_and_troop
        return self._play_deserter_for_flag(state, card, reclaim_flag, reclaim_card)

    def _play_traitor(
        self, state: GameState, card: TacticGuileCard
    ) -> Optional[GameState]:
        assert card.get_tactics() == TacticGuiles.TRAITOR
        flag_and_troop = self._choose_deployed_troops(state, self.get_opposite_id())
        if flag_and_troop is None:
            return None
        reclaim_flag, reclaim_card = flag_and_troop
        redeploy_flag = self._choose_flag_to_deploy(state, reclaim_card)
        return self._play_redeploy_for_flag(
            state, card, reclaim_flag, reclaim_card, redeploy_flag,
        )

    def _choose_deployed_troops(
        self, state: GameState, player: int, troops_only: bool = False
    ) -> Optional[Tuple[Flag, TroopAndTacticMoraleCard]]:
        flags = state.get_flags()
        while True:
            print("choose the flag: ")
            input_candidates = [0]
            for i, f in enumerate(flags):
                stacked_cards_of_flag = f.get_stacked_cards(player)
                stack_cards_repr = ", ".join([repr(c) for c in stacked_cards_of_flag])
                if f.is_resolved():
                    print(f"[-]: resolved, {stack_cards_repr}")
                else:
                    input_candidates.append(i + 1)
                    print(f"[{i + 1}]: {stack_cards_repr}")
            print("[0]: return to select the card to play")
            flag_index = await_user_num(input_candidates)
            if flag_index == 0:
                return None
            flag = flags[flag_index - 1]
            cards = flag.get_stacked_cards(player)
            print("choose the card: ")
            input_candidates = [0]
            for i, c in enumerate(cards):
                if troops_only and isinstance(c, TacticCard):
                    print(f"[x]: {repr(c)}")
                else:
                    print(f"[{i + 1}]: {repr(c)}")
                    input_candidates.append(i + 1)
            print("[0]: return to select the flag")
            card_index = await_user_num(input_candidates)
            if card_index == 0:
                continue
            return flag, cards[card_index - 1]

    def _draw_deck(self, state: GameState) -> Optional[Card]:
        troops_deck = state.get_troops_deck()
        tactics_deck = state.get_tactics_deck()
        draw_troops = troops_deck.is_remain()
        draw_tactics = tactics_deck.is_remain()
        if draw_troops and draw_tactics:
            print("draw card from?")
            print(f"[0] -- troops deck, remains {len(troops_deck)} cards")
            print(f"[1] -- tactics deck, remains {len(tactics_deck)} cards")
            if await_user_num([0, 1]) == 0:
                draw_tactics = False
            else:
                draw_troops = False
        if draw_troops:
            return troops_deck.draw()
        if draw_tactics:
            return tactics_deck.draw()
        # both decks are empty
        return None


def await_user_num(candidate: Iterable[int]) -> int:
    return int(await_user_input([str(i) for i in candidate]))


def await_user_input(
    candidate: Optional[Collection[str]] = None, msg: Optional[str] = None,
) -> str:
    while True:
        code = input(msg or f"Input one of {repr(candidate)} :")
        if candidate is None or not candidate or code in candidate:
            return code
        print("invalid input.")

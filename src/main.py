#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
from typing import Callable, Dict, Iterable, List, Tuple

from src.cards.cards import Card
from src.consts import PLAYER_UNRESOLVED
from src.gamestate import GameState
from src.players.player import Player
from src.resolver import resolve


class Game:
    @staticmethod
    def new(
        state: GameState,
        player_factories: Tuple[
            Callable[[int, Iterable[Card]], Player],
            Callable[[int, Iterable[Card]], Player],
        ],
        shuffle_deck: bool = True,
    ) -> "Game":
        if shuffle_deck:
            state.get_tactics_deck().shuffle()
            state.get_troops_deck().shuffle()
        players = [
            factory(i, [state.get_troops_deck().draw() for _ in range(7)])
            for i, factory in enumerate(player_factories)
        ]
        return Game(state, tuple(players))  # type: ignore

    def __init__(self, state: GameState, players: Tuple[Player, Player]) -> None:
        self._winner = PLAYER_UNRESOLVED
        self._turn_length = 0
        self._state = state
        self._players = players

    def get_turn_length(self) -> int:
        return self._turn_length

    def get_winner(self) -> int:
        return self._winner

    def run(self) -> int:
        if self._winner != PLAYER_UNRESOLVED:
            return self._winner
        self._turn_length += 1
        for p in self._players:
            # player action
            self._state = p.play(self._state)
            # resolve flag state
            resolve(self._state)
            # check winner
            self._winner = self._state.get_winner()
            if self._winner != PLAYER_UNRESOLVED:
                return self._winner
        return PLAYER_UNRESOLVED


def watch_main(arg: List[str]) -> None:
    pass


def vscpu_main(arg: List[str]) -> None:
    pass


def vshuman_main(arg: List[str]) -> None:
    pass


def train_main(arg: List[str]) -> None:
    pass


def _await_user_input() -> None:
    input("Press enter to continue...")


def _get_prog_mode_dict() -> Dict[str, Callable[[List[str]], None]]:
    ret_dict: Dict[str, Callable[[List[str]], None]] = {}
    items = globals().items()
    for key, entry in items:
        if key.endswith("_main"):
            label = key[:-5]
            ret_dict[label] = entry
    return ret_dict


if __name__ == "__main__":
    modes = _get_prog_mode_dict()
    parser = argparse.ArgumentParser(description="Python BattleLine implementation")
    parser.add_argument("mode", choices=list(modes.keys()))
    args, remainder = parser.parse_known_args()
    modes[args.mode](remainder)

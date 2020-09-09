#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
from typing import Callable, Dict, List, Tuple

from src.consts import PLAYER_A, PLAYER_B, PLAYER_UNRESOLVED
from src.gamestate import GameState
from src.players.humanplayer import HumanPlayer
from src.players.player import Player
from src.resolver import resolve


class Game:
    def __init__(self, state: GameState, players: Tuple[Player, Player]) -> None:
        self._winner = PLAYER_UNRESOLVED
        self._turn_length = 0
        self._state = state
        self._players = players

    def get_state(self) -> GameState:
        return self._state

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
            print(repr(self._state))
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
    game = Game(GameState.new(), (HumanPlayer(PLAYER_A), HumanPlayer(PLAYER_B)))
    while game.run() == PLAYER_UNRESOLVED:
        pass
    print(f"Player {game.run() + 1} win!")
    print(repr(game.get_state()))


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

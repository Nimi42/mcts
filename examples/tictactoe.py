from __future__ import division, annotations

import operator
from copy import deepcopy
from functools import reduce
from typing import List, Generator
import numpy as np
from mcts.legacy import MCTS, State


class Action:
    def __init__(self, player: int, x: int, y: int):
        self.player = player
        self.x = x
        self.y = y

    def __str__(self):
        return str((self.x, self.y))

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.x == other.x and
                self.y == other.y and
                self.player == other.player)

    def __hash__(self):
        return hash((self.x, self.y, self.player))


class TicTacToe(State):

    def __init__(self, board: List[List[int]], turn: int,  current_player: int):
        self.board = board
        self.board_turn = turn
        self.current_player = current_player

        def action_gen() -> Generator[Action, None, None]:
            random = np.random.choice(9, 9, replace=False)
            actions = []
            for idx in random:
                i, j = np.unravel_index(idx, (3, 3))
                if self.board[i][j] == 0:
                    action = Action(player=self.current_player, x=i, y=j)
                    actions.append(action)
                    new_state = self.take_action(action)
                    if (new_state.get_reward() < 0 and self.current_player != self.board_turn or
                            new_state.get_reward() > 1 and self.current_player == self.board_turn):
                        yield action
                        return
            for action in actions:
                yield action

        self._unexplored = action_gen()

    def get_unexplored_actions(self) -> Generator[Action, None, None]:
        return self._unexplored

    def get_best_action(self):
        random = np.random.choice(9, 9, replace=False)
        for idx in random:
            i, j = np.unravel_index(idx, (3, 3))
            if self.board[i][j] == 0:
                return Action(player=self.current_player, x=i, y=j)

    def take_action(self, action: Action) -> TicTacToe:
        new_board = deepcopy(self.board)
        new_board[action.x][action.y] = action.player
        return TicTacToe(new_board, self.board_turn, self.current_player * -1)

    def is_terminal(self) -> bool:
        for row in self.board:
            if abs(sum(row)) == 3:
                return True
        for column in list(map(list, zip(*self.board))):
            if abs(sum(column)) == 3:
                return True
        for diagonal in [[self.board[i][i] for i in range(len(self.board))],
                         [self.board[i][len(self.board) - i - 1] for i in range(len(self.board))]]:
            if abs(sum(diagonal)) == 3:
                return True
        return reduce(operator.mul, sum(self.board, []), 1) == 1

    def get_reward(self) -> int:
        for row in self.board:
            if abs(sum(row)) == 3:
                return sum(row) // 3 * self.board_turn
        for column in list(map(list, zip(*self.board))):
            if abs(sum(column)) == 3:
                return sum(column) // 3 * self.board_turn
        for diagonal in [[self.board[i][i] for i in range(len(self.board))],
                         [self.board[i][len(self.board) - i - 1] for i in range(len(self.board))]]:
            if abs(sum(diagonal)) == 3:
                return sum(diagonal) // 3 * self.board_turn
        return 0


if __name__ == '__main__':
    def run_example():
        state = TicTacToe([[0, 0, 0], [0, 0, 0], [0, 0, 0]], 1, 1)
        mcts = MCTS(time_limit=300)
        while not state.is_terminal():

            action = mcts.search(state)
            state = state.take_action(action)

            state.board_turn = state.board_turn * -1
            for i in state.board:
                print(i)
            print('---')

    run_example()
    # import timeit
    # print(timeit.timeit('run_example()', setup="from __main__ import run_example", number=5))

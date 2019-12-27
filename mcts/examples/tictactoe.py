from __future__ import division, annotations

import operator
from collections import deque
from copy import deepcopy
from functools import reduce
from typing import List

import numpy as np


class TicTacToe:

    def __init__(self, board: List[List[int]], turn: int,  current_player: int):
        self.board = board
        self.board_turn = turn
        self.current_player = current_player
        self._unexplored = None

    def __iter__(self):
        return self

    def __next__(self):
        if self._unexplored is None:
            self._random = iter(np.random.choice(9, 9, replace=False))
            self._unexplored = []

        for idx in self._random:
            i, j = np.unravel_index(idx, (3, 3))


            if self.board[i][j] == 0:
                action = str(i) + str(j)
                self._unexplored.append(action)
                new_state = self.take_action(action)

                if (new_state.get_reward() < 0 and self.current_player != self.board_turn or
                        new_state.get_reward() > 0 and self.current_player == self.board_turn):
                    self._unexplored = []
                    deque(self._random, maxlen=0)

                    return action

        if self._unexplored:
            return self._unexplored.pop(0)
        raise StopIteration

    def get_proposed_action(self):
        random = np.random.choice(9, 9, replace=False)

        for idx in random:
            i, j = np.unravel_index(idx, (3, 3))
            if self.board[i][j] == 0:
                action = str(i) + str(j)
                new_state = self.take_action(action)
                if (new_state.get_reward() < 0 and self.current_player != self.board_turn or
                        new_state.get_reward() > 0 and self.current_player == self.board_turn):

                    return action

        return action

    def take_action(self, action: str) -> TicTacToe:
        new_board = deepcopy(self.board)
        new_board[int(action[0])][int(action[1])] = self.current_player
        ret = TicTacToe(new_board, self.board_turn, self.current_player * -1)
        return ret

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

    def __str__(self):
        return "----------------\n| %2d | %2d | %2d |\n| %2d | %2d | %2d |\n| %2d | %2d | %2d |\n----------------\n" % \
               tuple([j for i in self.board for j in i])


if __name__ == '__main__':
    # def run_example():
    #     from legacy import MCTS
    #     state = TicTacToe([[0, 0, 0], [0, 0, 0], [0, 0, 0]], 1, 1)
    #     mcts = MCTS(iteration_limit=5000)
    #     while not state.is_terminal():
    #         action = mcts.search(state)
    #         state = state.take_action(action)
    #         state.board_turn = state.board_turn * -1
    #         # for i in state.board:
    #         #     print(i)
    #         # print('---')
    # #
    # #
    # #run_example()
    # import timeit
    # print(timeit.timeit('run_example()', setup="from __main__ import run_example", number=10) / 10)

    import backend

    def run_c():
        state = TicTacToe([[0, 0, 0], [0, 0, 0], [0, 0, 0]], 1, 1)

        while not state.is_terminal():
            action = backend.search(state)
            state = state.take_action(action)
            state.board_turn = state.board_turn * -1


    run_c()

    # import timeit
    # print(timeit.timeit('run_c()', setup="from __main__ import run_c", number=10) / 10)

    # import backend
    # state = TicTacToe([[0, 0, 0], [0, 0, 0], [0, 0, 0]], 1, 1)
    #
    # result = backend.search(state)
    # print(result)

    # import objgraph
    # import backend
    #
    # objgraph.show_growth(limit=10)
    # state = TicTacToe([[0, 0, 0], [0, 0, 0], [0, 0, 0]], 1, 1)
    #
    # result = backend.search(state)
    # state = state.take_action(result)
    #
    # objgraph.show_growth()
    # roots = objgraph.get_leaking_objects()
    # objgraph.show_most_common_types(objects=roots)
    # objgraph.show_refs(roots[:20], refcounts=True, filename='roots.png')
    # objgraph.show_backrefs(objgraph.by_type('TicTacToe'), refcounts=True, filename='refcounts.png')
from __future__ import division, annotations

import time
import math
import random
from typing import Dict, Callable, Any, List, Type

from abc import ABC, abstractmethod


class State(ABC):

    @abstractmethod
    def get_random_action(self) -> List[Any]:
        pass

    @abstractmethod
    def get_possible_actions(self) -> List[Any]:
        pass

    @abstractmethod
    def take_action(self, action: Any) -> Type[State]:
        pass

    @abstractmethod
    def is_terminal(self) -> bool:
        pass

    @abstractmethod
    def get_reward(self) -> Any:
        # only needed for terminal states
        pass


class Node:
    def __init__(self, state: Type[State], parent):
        self.state: Type[State] = state
        self.is_terminal: bool = state.is_terminal()
        self.is_fully_expanded: bool = self.is_terminal
        self.parent: Node = parent
        self.num_visits: int = 0
        self.total_reward: int = 0
        self.children: Dict[Node] = {}


class MCTS:

    def __init__(self, *,
                 time_limit: int = None,
                 iteration_limit: int = None,
                 exploration_constant: float = math.sqrt(2)):
        if time_limit is not None:
            if iteration_limit is not None:
                raise ValueError("Cannot have both a time limit and an iteration limit")
            # time taken for each MCTS search in milliseconds
            self.time_limit = time_limit
            self.limit_type = 'time'
        else:
            if iteration_limit is None:
                raise ValueError("Must have either a time limit or an iteration limit")
            # number of iterations of the search
            if iteration_limit < 1:
                raise ValueError("Iteration limit must be greater than one")
            self.search_limit = iteration_limit
            self.limit_type = 'iterations'

        self.explorationConstant = exploration_constant


    def search(self, initial_state: Type[State]) -> Any:
        self.root: Node = Node(initial_state, None)
        if self.limit_type == 'time':
            # Change to timeout without polling?
            time_limit = time.time() + self.time_limit / 1000
            while time.time() < time_limit:
                self._execute_round()
        else:
            for _ in range(self.search_limit):
                self._execute_round()

        best_child = self._get_best_child(self.root, 0)
        return self._get_action(self.root, best_child)

    def _execute_round(self) -> None:
        node = self._select_node(self.root)
        reward = self._rollout(node.state)
        self._backpropogate(node, reward)

    def _select_node(self, node: Node) -> Node:
        while not node.is_terminal:
            if node.is_fully_expanded:
                node = self._get_best_child(node, self.explorationConstant)
            else:
                result = self._expand(node)
                if result is not None:
                    return result
        return node

    def _expand(self, node: Node) -> Node:
        actions = node.state.unexplored
        for action in actions:
            if action not in node.children:
                new_node = Node(node.state.take_action(action), node)
                node.children[action] = new_node
                return new_node
        node.is_fully_expanded = True
        return None

    def _rollout(self, state: Type[State]) -> Any:
        while not state.is_terminal():
            try:
                action = state.get_random_action()
            except IndexError:
                raise Exception("Non-terminal state has no possible actions: " + str(state))
            state = state.take_action(action)
        return state.get_reward()

    def _backpropogate(self, node: Node, reward: Any) -> None:
        while node is not None:
            node.num_visits += 1
            node.total_reward += reward
            node = node.parent

    def _get_best_child(self, node: Node, exploration_value) -> Node:
        best_value = float("-inf")
        best_nodes = []

        for child in node.children.values():
            node_value = child.total_reward / child.num_visits + exploration_value * math.sqrt(
                2 * math.log(node.num_visits) / child.num_visits)
            if node_value > best_value:
                best_value = node_value
                best_nodes = [child]
            elif node_value == best_value:
                best_nodes.append(child)
        return random.choice(best_nodes)

    def _get_action(self, root: Node, best_child: Node) -> Any:
        result = None
        for action, node in root.children.items():
            if node is best_child:
                result = action
                break
        return result

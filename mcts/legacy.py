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


class ActionInterface(ABC):

    @abstractmethod
    def __eq__(self, other):
        pass

    @abstractmethod
    def __hash__(self):
        pass


def random_policy(state: Type[State]) -> Any:
    while not state.is_terminal():
        try:
            action = state.get_random_action()
        except IndexError:
            raise Exception("Non-terminal state has no possible actions: " + str(state))
        state = state.take_action(action)
    return state.get_reward()


class TreeNode:
    def __init__(self, state: Type[State], parent):
        self.state: Type[State] = state
        self.is_terminal: bool = state.is_terminal()
        self.is_fully_expanded: bool = self.is_terminal
        self.parent: TreeNode = parent
        self.num_visits: int = 0
        self.total_reward: int = 0
        self.children: Dict[TreeNode] = {}


class MCTS:

    def __init__(self, initial_state: Type[State], *,
                 time_limit: int = None,
                 iteration_limit: int = None,
                 exploration_constant: float = math.sqrt(2),
                 rollout_policy: Callable[[Type[State]], Any] = random_policy):
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
        self.rollout = rollout_policy
        self.root: TreeNode = TreeNode(initial_state, None)

    def search(self) -> Any:
        if self.limit_type == 'time':
            # Change to timeout without polling?
            time_limit = time.time() + self.time_limit / 1000
            while time.time() < time_limit:
                self.execute_round()
        else:
            for _ in range(self.search_limit):
                self.execute_round()

        best_child = self.get_best_child(self.root, 0)
        return self.get_action(self.root, best_child)

    def execute_round(self) -> None:
        node = self.select_node(self.root)
        reward = self.rollout(node.state)
        self.backpropogate(node, reward)

    def select_node(self, node: TreeNode) -> TreeNode:
        while not node.is_terminal:
            if node.is_fully_expanded:
                node = self.get_best_child(node, self.explorationConstant)
            else:
                result = self.expand(node)
                if result is not None:
                    return result
        return node

    def expand(self, node: TreeNode) -> TreeNode:
        actions = node.state.unexplored
        for action in actions:
            if action not in node.children:
                new_node = TreeNode(node.state.take_action(action), node)
                node.children[action] = new_node
                #if len(actions) == len(node.children):
                    #node.is_fully_expanded = True
                return new_node
        node.is_fully_expanded = True
        return None

    def backpropogate(self, node: TreeNode, reward: Any) -> None:
        while node is not None:
            node.num_visits += 1
            node.total_reward += reward
            node = node.parent

    def get_best_child(self, node: TreeNode, exploration_value) -> TreeNode:
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

    def get_action(self, root: TreeNode, best_child: TreeNode) -> Any:
        result = None
        for action, node in root.children.items():
            if node is best_child:
                result = action
                break
        return result

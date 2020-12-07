import numpy as np
from src import config
from src.mcts.node import Node
from copy import deepcopy
from src.utils.utils import softmax


class MCTS(object):
    """
    蒙特卡洛树的实现
    """

    def __init__(self, model):
        self.model = model
        # user simulation_num to search mcts for one position
        self.simulation_num = config.per_search_simulation_num
        self.root = Node(None, 1.)

    def get_actions(self, board, t=1e-3):
        for i in range(self.simulation_num):
            board_tmp = deepcopy(board)
            self._search(board_tmp)
        action_visites = [(action, node.n) for action, node in self.root.childrens.items()]
        actions, visites = zip(*action_visites)
        if hasattr(self.model, 'pure_mcts'):
            # 概率就等于访问数量 不需要计算softmax 选择访问次数最大的
            probs = visites
        else:
            probs = softmax(1.0 / t * np.log(np.array(visites)) + 1e-10)
        return np.array(actions), probs

    def _search(self, board):
        """
        more detail see mcts/mcts.png
        :param board:
        :return:
        """
        node = self.root
        while True:
            if node.is_leaf:
                break
            # 1 choose max upper confidence bound --> ucb
            action, node = node.select()
            # st -> st+1 change state
            board.move(action)

        probs, values = self.model.policy_value(board)
        probs, values = np.squeeze(probs), np.squeeze(values)
        actions = board.availables
        action_probs = probs[list(actions)]
        is_end, player = board.is_end
        if hasattr(self.model, 'pure_mcts'):
            if not is_end:
                node.expansion(list(zip(actions, action_probs)))
            value = self._rollout(board)
        else:
            if not is_end:
                node.expansion(list(zip(actions, action_probs)))
                # 用神经网络的value来更新权重
                value = values
            else:
                if player == -1:
                    value = 0.
                else:
                    value = 1 if player == board.current_player else -1
        # update value
        node.update(value)

    def _rollout(self, board):
        current_player = board.current_player
        while True:
            is_end, player = board.is_end
            if is_end:
                break
            # random 快速走子
            index = np.random.randint(len(board.availables))
            action = list(board.availables)[index]
            board.move(action)
        if is_end:
            if player == -1:
                value = 0.
            else:
                value = 1 if player == current_player else -1
        return value

    def do_action(self, action):
        if action in self.root.childrens.keys():
            self.root = self.root.childrens[action]
            self.root.parent = None

    def reset_action(self, board, action):
        node = self.root
        if len(node.childrens) == 0:
            probs, values = self.model.policy_value(board)
            probs, values = np.squeeze(probs), np.squeeze(values)
            actions = list(board.availables)
            action_probs = probs[list(actions)]
            node.expansion(list(zip(actions, action_probs)))
            self.do_action(action)

    def reset(self):
        # rest mct
        self.root = Node(None, 1.)
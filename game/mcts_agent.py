import random
import math
from copy import deepcopy
import threading

class MCTSAgent:
    def __init__(self, game, player_num):
        self.game = game
        self.player_num = player_num
        self.root = None
        self.start_pos = None
        self.target_pos = None
        self.pos_found = False
        self.need_send_comm_to_robot = False
        
    class Node:
        class State:
            def __init__(self, last_begin, last_end, last_path, board, turn):
                self.last_begin = last_begin
                self.last_end = last_end
                self.last_path = last_path
                self.board = board
                self.turn = turn
                
        def __init__(self, state, parent=None):
            self.state = state  # 当前状态（棋盘状态）
            self.parent = parent  # 父节点
            self.children = []  # 子节点
            self.visits = 0  # 访问次数
            self.wins = 0  # 胜利次数
        
        def ucb(self):
            """计算该节点的 UCB1 值，用于选择最大 UCB 值的节点"""
            if self.visits == 0:
                return float('inf')  # 避免除以0，初次访问的节点的 UCB 值很大
            return self.wins / self.visits + math.sqrt(2 * math.log(self.parent.visits) / self.visits)
    
    def select(self, node):
        """选择最优节点（最大化 UCB1 值）"""
        while node.children:
            node = max(node.children, key=lambda child: child.ucb())
        return node

    def expand(self, node):
        """扩展节点"""
        for (q, r), value in node.state.board.items():
          if value == self.player_num:
            moves, paths = self.game.getValidMoves(node.state.board, q, r)
            for move in moves:
                path = next((p for p in paths if p[-1] == move), None)
                new_board = deepcopy(node.state.board)
                new_turn = deepcopy(node.state.turn)
                new_board = self.game.movePos(new_board, (q,r), move)
                _, new_turn = self.game.toggleTurn(new_turn)
                new_state = self.Node.State((q,r), move, path, new_board, new_turn)
                node.children.append(self.Node(new_state, parent=node))
    
    def simulate(self, node):
        """进行随机模拟"""
        simulated_state = deepcopy(node.state)
        game_over = False
        winner = None
        current_board = simulated_state.board
        current_turn = simulated_state.turn
        i = 0
        while not game_over:
            i = i + 1
            valid_choices = []
            for (q, r), value in current_board.items():
              if value == current_turn:
                moves, _ = self.game.getValidMoves(current_board, q, r)
                if moves:
                    for move in moves:
                        score = self.game.getScore(current_board, (q,r), move, current_turn)
                        valid_choices.append(((q,r), move, score))
            if random.random() < 0:
                random_move = random.choice(valid_choices)
            else:
                random_move = max(valid_choices, key = lambda x: x[2])
            current_board = self.game.movePos(current_board, random_move[0], random_move[1])
            _, current_turn = self.game.toggleTurn(current_turn)
            game_over, winner = self.game.checkWinner(current_board)
            if i > 150:
                break
        return winner

    def backpropagate(self, node, result):
        """反向传播"""
        while node:
            node.visits += 1
            if node.state.turn == result:
                node.wins += 1
            else:
                node.wins -= 1
            node = node.parent

    def get_best_move(self, state):
        """获取最优动作"""
        self.root = self.Node(state)
        self.root.visits = 1  # 根节点首先被访问一次
        for i in range(100):  # 模拟次数
            selected_node = self.select(self.root)    # 选择
            self.expand(selected_node)                # 扩展
            result = self.simulate(selected_node)     # 模拟
            self.backpropagate(selected_node, result) # 回溯
        
        best_node = max(self.root.children, key=lambda child: child.visits)
        return best_node.state.last_begin, best_node.state.last_end, best_node.state.last_path 
    
    def get_best_move_dev(self, state):
        valid_choice = []
        for (q, r), value in state.board.items():
            if value == state.turn:
                self.game.selected_pos = (q, r)
                moves, paths = self.game.getValidMoves(state.board, q, r)
                if moves:
                    for move in moves:
                        score = self.game.getScore(state.board, (q,r), move, state.turn)
                        valid_path = None
                        for path in paths:
                            if path[-1] == move:
                              valid_path = path
                              break  
                        valid_choice.append(((q,r), move, score, path))
        if random.random() < 0:
            random_move = random.choice(valid_choice)
        else:
            random_move = max(valid_choice, key = lambda x: x[2])
        return random_move[0], random_move[1], random_move[3]
        
        
    def run(self):
        # print("ai is runing")
        print(self.need_send_comm_to_robot)
        if (not self.game.game_over) and (not self.game.ai_ok) and \
            (self.game.current_turn == self.player_num) and (not self.pos_found):
            # print("searching...")
            board = self.game.board
            current_turn = self.game.current_turn
            current_state = self.Node.State(None, None, None, board, current_turn)
            selected, goal, path = self.get_best_move_dev(current_state)
            self.start_pos = self.game.real_board.get[selected]
            self.target_pos = self.game.real_board.get[goal]
            self.need_send_comm_to_robot = True
            self.game.selected_pos = selected
            self.game.need_draw_path = True
            self.game.draw_path = path
            self.game.movePos(self.game.board, selected, goal)
            self.pos_found = True
            # print("finished")
        else:
            self.start_pos = None
            self.target_pos = None
            self.need_send_comm_to_robot = False
        threading.Timer(0.2, self.run).start()
        

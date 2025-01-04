import random
import math
from copy import deepcopy
import threading

class MCTSAgent:
    def __init__(self, app, player_num, is_playing_simulation):
        self.app = app
        self.player_num = player_num
        self.is_playing_simulation = is_playing_simulation
        self.root = None
        self.start_pos = None
        self.target_pos = None
        self.comm_sent = False
        self.need_send_comm_to_robot = False
        self.first_move = True
        
    class Node:
        class State:
            def __init__(self, last_begin, last_end, last_path, board, player):
                self.last_begin = last_begin
                self.last_end = last_end
                self.last_path = last_path
                self.board = board
                self.player = player
                
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
            moves, paths = self.app.getValidMoves(node.state.board, q, r)
            for move in moves:
                path = next((p for p in paths if p[-1] == move), None)
                new_board = deepcopy(node.state.board)
                next_player = deepcopy(node.state.player)
                new_board = self.app.movePos(new_board, (q,r), move)
                next_player = self.app.switchTurn(next_player)
                new_state = self.Node.State((q,r), move, path, new_board, next_player)
                node.children.append(self.Node(new_state, parent=node))
    
    def simulate(self, node):
        """进行随机模拟"""
        simulated_state = deepcopy(node.state)
        game_over = False
        winner = None
        current_board = simulated_state.board
        current_player = simulated_state.player
        i = 0
        while not game_over:
            i = i + 1
            valid_choices = []
            for (q, r), value in current_board.items():
              if value == current_player:
                moves, _ = self.app.getValidMoves(current_board, q, r)
                if moves:
                    for move in moves:
                        score = self.app.getScoreMove(current_board, (q,r), move, current_player)
                        valid_choices.append(((q,r), move, score))
            if random.random() < 0.2:
                random_move = random.choice(valid_choices)
            else:
                random_move = max(valid_choices, key = lambda x: x[2])
            current_board = self.app.movePos(current_board, random_move[0], random_move[1])
            current_player = self.app.switchTurn(current_player)
            game_over, winner = self.app.checkWinner(current_board)
            if i > 70:
                max_score = -1
                max_player = None
                for player in self.app.getPlayerList():
                    temp_socre = self.app.getScoreBoard(current_board, player)
                    if temp_socre > max_score:
                        max_score = temp_socre
                        max_player = player
                winner = max_player
        return winner

    def backpropagate(self, node, result):
        """反向传播"""
        while node:
            node.visits += 1
            if node.state.player == result:
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
        return best_node.state.last_begin, best_node.state.last_end
    
    def get_best_move_dev(self, state):
        valid_choice = []
        for (q, r), value in state.board.items():
            if value == state.player:
                self.app.selected_pos = (q, r)
                moves, paths = self.app.getValidMoves(state.board, q, r)
                if moves:
                    for move in moves:
                        score1 = self.app.getScoreMove(state.board, (q,r), move, state.player)
                        board = deepcopy(state.board)
                        board[(q,r)] = 0
                        board[move] = state.player
                        score2 = self.app.getScoreBoard(board, state.player)
                        score = score1 + score2
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
        return random_move[0], random_move[1]
        
        
    def run(self):
        # print("ai is runing")
        if (not self.app.game_over) and (not self.app.ai_ok) and \
            (self.app.current_player == self.player_num) and (not self.comm_sent):
            print("searching...")
            board = self.app.board
            current_player = self.player_num
            current_state = self.Node.State(None, None, None, board, current_player)
            if self.first_move:
                selected, goal = self.get_best_move_dev(current_state)
                # self.first_move = False
            else:
                selected, goal = self.get_best_move(current_state)
                
            self.app.playerSelect(selected[0], selected[1], is_ai=True)
            self.app.playerSelect(goal[0], goal[1], is_ai=True)
            if not self.is_playing_simulation:
                self.start_pos = self.app.real_board.get(selected)
                self.target_pos = self.app.real_board.get(goal)
                self.need_send_comm_to_robot = True
                self.comm_sent = True
            else:
                self.app.ai_ok = True
            print(f"finished, {selected, goal}")
            
        else:
            self.start_pos = None
            self.target_pos = None
            self.need_send_comm_to_robot = False
        threading.Timer(0.2, self.run).start()
        

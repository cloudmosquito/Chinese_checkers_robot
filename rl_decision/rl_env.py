import numpy as np
import tkinter as tk
import sys
sys.path.append('E:\\OriginalF\\Undergraduate\\automatition_practice\\Chinese_chess_robot')
from game.chinese_chess_play import ChineseCheckersApp

class CheckersEnv:
    def __init__(self, app):
        self.app = app
        self.reset()

    def reset(self):
        """重置环境并返回初始状态"""
        self.app = ChineseCheckersApp(tk.Tk(), self.app.player_num, self.app.game_mode)
        return self.get_state()

    def get_state(self):
        """将棋盘转换为状态"""
        state = np.zeros((17, 17), dtype=int)
        for (q, r), value in self.app.board.items():
            state[q + 8, r + 8] = value
        return state.flatten()  # 或保持二维形式

    def getValidActions(self, player):
        actions = []
        for (q,r), value in self.app.board.items():
            if value == player:
                valid_moves, _ = self.app.getValidMoves(q, r)
                if valid_moves:
                    actions.append((q,r,valid_moves))
        return actions
    def step(self, action, player):
        """
        执行给定动作
        action: tuple (start_q, start_r, end_q, end_r)
        """
        start, end = action[:2], action[2:]
        if start in self.app.board and self.board[start] == player and \
            end in self.app.getValidMoves(*start)[0]:
            self.app.movePos(start, end)
            reward = self.calculate_reward(start, end)
            done = self.app.game_over
            return self.get_state(), reward, done
        return self.get_state(), -10, False  # 非法动作

    def calculate_reward(self, start, end):
        """定义奖励函数"""
        if self.app.game_over and self.app.winner == self.app.current_turn:
            return 100
        if end in self.app.home_pos.get(self.app.current_turn, []):
            return 10
        return 1  # 合法移动奖励

    def render(self):
        """可选：在终端或图形界面中渲染棋盘"""
        self.app.drawBoard()

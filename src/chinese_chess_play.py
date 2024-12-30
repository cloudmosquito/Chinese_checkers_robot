import tkinter as tk
from tkinter import messagebox
import math
from enum import Enum
import queue

# 坐标转换工具类
def cartesian2Oblique(x, y):
    """将直角坐标转换为斜坐标。"""
    q = x - y / math.sqrt(3)
    r = 2 * y / math.sqrt(3)
    return round(q), round(r)

def oblique2Cartesian(q, r):
    """将斜坐标转换为直角坐标。"""
    x = q + 0.5 * r
    y = (math.sqrt(3) / 2) * r
    return x, y

# 检查斜坐标是否合法
def isValidOblique(q, r):
    """检查给定的斜坐标是否是合法的棋盘点。"""
    valid_positions = {
        -8: [4],
        -7: [3, 4],
        -6: [2, 3, 4],
        -5: [1, 2, 3, 4],
        -4: list(range(-4, 9)),
        -3: list(range(-4, 8)),
        -2: list(range(-4, 7)),
        -1: list(range(-4, 6)),
         0: list(range(-4, 5)),
         1: list(range(-5, 5)),
         2: list(range(-6, 5)),
         3: list(range(-7, 5)),
         4: list(range(-8, 5)),
         5: [-4, -3, -2, -1],
         6: [-4, -3, -2],
         7: [-4, -3],
         8: [-4]
    }
    return r in valid_positions.get(q, [])

def isValidInitOblique(player, q, r):
    valid_init_oblique_1 = {
        1: [-5],
        2: [-6, -5],
        3: [-7, -6, -5],
        4: [-8, -7, -6, -5],
    }
    valid_init_oblique_2 = {
        -4: [5, 6, 7, 8],
        -3: [5, 6, 7],
        -2: [5, 6],
        -1: [5],
    }
    if player == 1:
        return r in valid_init_oblique_1.get(q, [])
    elif player == -1:
        return r in valid_init_oblique_2.get(q, [])
    else:
        return False

# 创建棋盘
class ChineseCheckersApp:
    class Turn(Enum):
        PLAYER1_TURN = 0
        PLAYER2_TURN = 1
        WAITING1_TURN = 2
        WAITING2_TURN = 3
        AI_TURN = -1
    class GameMode(Enum):
        PVP = 0
        PVE = 1
    
    def __init__(self, master, game_mode=GameMode.PVE):
        self.game_mode = game_mode
        self.current_turn = ChineseCheckersApp.Turn.PLAYER1_TURN
        self.selected_piece = None
        self.valid_moves = []
        
        self.master = master
        self.master.title("Chinese Checkers")
        self.board = self.create_chinese_checkers_board()
        self.canvas = tk.Canvas(self.master, width=600, height=600)
        self.canvas.pack()
        # 用于指示当前轮次的圆圈
        self.turn_indicator = self.canvas.create_oval(550, 10, 590, 50, fill="red")
        self.draw_board()
        self.canvas.bind("<Button-1>", self.handle_click)
        self.valid_positions = {
        -8: [4],
        -7: [3, 4],
        -6: [2, 3, 4],
        -5: [1, 2, 3, 4],
        -4: list(range(-4, 9)),
        -3: list(range(-4, 8)),
        -2: list(range(-4, 7)),
        -1: list(range(-4, 6)),
         0: list(range(-4, 5)),
         1: list(range(-5, 5)),
         2: list(range(-6, 5)),
         3: list(range(-7, 5)),
         4: list(range(-8, 5)),
         5: [-4, -3, -2, -1],
         6: [-4, -3, -2],
         7: [-4, -3],
         8: [-4]
    }

        
    def create_chinese_checkers_board(self):
        """创建初始棋盘，使用斜坐标系标记点。"""
        board = {}
        for q in range(-8, 9):
            for r in range(-8, 9):
                if isValidOblique(q, r):
                    board[(q, r)] = 0  # 空点

        # 初始化玩家棋子
        for q in range(-8, 9):
            for r in range(-8, 9):
                if isValidInitOblique(1, q, r):
                    board[(q, r)] = 1  # 玩家 1

        for q in range(-8, 9):
            for r in range(-8, 9):
                if isValidInitOblique(-1, q, r):
                    board[(q, r)] = -1  # 玩家 2
        return board

    def draw_board(self):
        self.canvas.delete("all")
        
        # 重新绘制轮次指示圆圈
        color = "red" if (self.current_turn == ChineseCheckersApp.Turn.PLAYER1_TURN \
            or self.current_turn == ChineseCheckersApp.Turn.WAITING1_TURN) else "blue"
        self.canvas.create_oval(555, 15, 585, 45, fill=color)
        
        for (q, r), value in self.board.items():
            x, y = oblique2Cartesian(q, r)
            screen_x = 300 + x * 40
            screen_y = 300 - y * 40
            color = "white" if value == 0 else ("red" if value == 1 else "blue")
            self.canvas.create_oval(screen_x - 15, screen_y - 15, screen_x + 15, screen_y + 15, fill=color)
            
            if self.selected_piece == (q, r):
                # 选中棋子：用小圆点高亮
                self.canvas.create_oval(screen_x - 5, screen_y - 5, screen_x + 5, screen_y + 5, fill="yellow")
            elif (q, r) in self.valid_moves:
                color = "red" if self.current_turn == ChineseCheckersApp.Turn.PLAYER1_TURN else "blue"
                self.canvas.create_rectangle(
                    screen_x - 20, screen_y - 20, screen_x + 20, screen_y + 20,
                    outline=color, width=2, dash=(4, 2)
                )

    def handle_click(self, event):
        
        print(self.current_turn)
        
        # 若当前是AI回合，屏蔽鼠标点击响应
        if self.current_turn == ChineseCheckersApp.Turn.AI_TURN:
            return

        clicked_x = (event.x - 300) / 40
        clicked_y = (300 - event.y) / 40
        q, r = cartesian2Oblique(clicked_x, clicked_y)

        if self.selected_piece:
            # 第二次点击：尝试移动或更换选中的棋子
            if (q, r) in self.valid_moves:  # 有效移动
                self.move_piece(self.selected_piece, (q, r))
                self.toggleTurn()
                self.selected_piece = None
                self.valid_moves = []
            elif self.board.get((q, r), 0) == (1 if self.current_turn == ChineseCheckersApp.Turn.PLAYER1_TURN else -1):
                # 更换选中的棋子
                self.selected_piece = (q, r)
                self.valid_moves = self.get_valid_moves(q, r)
        else:
            # 第一次点击：选择棋子
            if self.board.get((q, r), 0) == (1 if self.current_turn == ChineseCheckersApp.Turn.PLAYER1_TURN else -1):
                self.selected_piece = (q, r)
                self.valid_moves = self.get_valid_moves(q, r)

        self.draw_board()

    # 是否满足跳棋跳动规则：平行x轴线上
    def judge_x(self, q, r, temp_q):

        judge=True
        # 中间点在棋盘可行域上
        judge=  temp_q in self.valid_positions.get([], r)
        # 中间点不为空
        if self.board[(temp_q, r)]==0:
            judge=False
        # 起点与中间点之间全为空
        for dq in range(q, temp_q):
           if self.board[(dq, r)]!=0:
              judge=False
              break
        # 终点在棋盘可行域上
        judge=  2*temp_q-q in self.valid_positions.get([], r)
        # 终点与中间点之间全为空
        for dq in range(temp_q, 2*temp_q-q):
           if self.board[(dq, r)]!=0:
              judge=False
              break
        if judge:
           final_q=2*temp_q-q
           return [final_q,r]
    
    # 是否满足跳棋跳动规则：平行y轴线上
    def judge_y(self, q, r, temp_r):

        judge=True
        # 中间点在棋盘可行域上
        judge=  temp_r in self.valid_positions.get(q, [])
        # 中间点不为空
        if self.board[(q, temp_r)]==0:
            judge=False
        # 起点与中间点之间全为空
        for dr in range(r, temp_r):
           if self.board[(q, dr)]!=0:
              judge=False
              break
        # 终点在棋盘可行域上
        judge=  2*temp_r-r in self.valid_positions.get(q, [])
        # 终点与中间点之间全为空
        for dq in range(temp_r, 2*temp_r-r):
           if self.board[(q, dr)]!=0:
              judge=False
              break
        if judge:
           final_r=2*temp_r-r
           return [q,final_r]
            
    # 是否满足跳棋跳动规则：平行|x-y|轴线上
    def judge_y(self, q, r, temp_q, temp_r):

        judge=True
        # 中间点在棋盘可行域上
        judge=  temp_q in self.valid_positions.get([], temp_r)
        judge=  temp_r in self.valid_positions.get(temp_q, [])
        # 中间点在平行|x-y|轴线上
        if q+r!=temp_q+temp_r:
           judge=False
        # 中间点不为空
        if self.board[(temp_q, temp_r)]==0:
            judge=False
        # 起点与中间点之间全为空
        for dr in range(r, temp_r):
           if self.board[(q+r-dr, dr)]!=0:
              judge=False
        # 终点在棋盘可行域上
        judge=  2*temp_q-r in self.valid_positions.get([], r)
        judge=  2*temp_r-r in self.valid_positions.get(q, [])
        # 终点与中间点之间全为空
        for dq in range(temp_r, 2*temp_r-r):
           if self.board[(q, dr)]!=0:
              judge=False
        if judge:
           final_q=2*temp_q-q
           final_r=2*temp_r-r
           return [final_q,final_r]          

    # 搜索：移动，跳动，返回所有可行点
    def get_valid_moves_by_bfs(self, q, r,):
        moves = []
        # 移动一次
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, -1), (-1, 1)]
        for dq, dr in directions:
            nq, nr = q + dq, r + dr
            if isValidOblique(nq, nr) and self.board.get((nq, nr), 1) == 0:
                moves.append((nq, nr))
        
        temp_q in self.valid_positions.get([], r)

        temp_r in self.valid_positions.get(q, [])

        


        return moves
    
    
    def get_valid_moves(self, q, r):
        moves = []
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, -1), (-1, 1)]
        for dq, dr in directions:
            nq, nr = q + dq, r + dr
            if isValidOblique(nq, nr) and self.board.get((nq, nr), 0) == 0:
                moves.append((nq, nr))
        return moves

    def move_piece(self, begin, end):
        self.board[end] = self.board[begin]
        self.board[begin] = 0

    def ai_turn(self):
        # Placeholder for AI logic
        moves = []  # AI logic to find moves here
        if moves:
            start, end = moves[0]
            self.move_piece(start, end)
        self.draw_board()
        self.toggleTurn()
    
    def toggleTurn(self):
        if self.game_mode == ChineseCheckersApp.GameMode.PVE:
            if self.current_turn == ChineseCheckersApp.Turn.PLAYER1_TURN:
                self.current_turn = ChineseCheckersApp.Turn.AI_TURN
            else :
                self.current_turn = ChineseCheckersApp.Turn.PLAYER1_TURN
        else :
            if self.current_turn == ChineseCheckersApp.Turn.PLAYER1_TURN:
                self.current_turn = ChineseCheckersApp.Turn.PLAYER2_TURN
            else :
                self.current_turn = ChineseCheckersApp.Turn.PLAYER1_TURN

if __name__ == "__main__":
    root = tk.Tk()
    app = ChineseCheckersApp(root, ChineseCheckersApp.GameMode.PVP)
    root.mainloop()

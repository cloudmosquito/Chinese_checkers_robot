import tkinter as tk
from tkinter import messagebox
import math
from enum import Enum
from collections import deque

# 坐标转换工具
def cartesian2Oblique(x, y):
    """将直角坐标系转换为斜坐标系

    Args:
        x (float): 直角坐标系下的横坐标
        y (float): 直角坐标系下的纵坐标

    Returns:
        tuple(int, int): 斜坐标系下的横坐标和纵坐标
    """
    q = x - y / math.sqrt(3)
    r = 2 * y / math.sqrt(3)
    return round(q), round(r)

def oblique2Cartesian(q, r):
    """将斜坐标系转换为直角坐标系

    Args:
        q (int): 斜坐标系下的横坐标
        r (int): 斜坐标系下的纵坐标

    Returns:
        tuple(float, float): 直角坐标系下的横坐标和斜坐标
    """
    x = q + 0.5 * r
    y = (math.sqrt(3) / 2) * r
    return x, y

def oblique2Screen(q, r):
    """将斜坐标系转换为显示屏幕的直角坐标系

    Args:
        q (int): 斜坐标系下的横坐标
        r (int): 斜坐标系下的纵坐标

    Returns:
        tuple(float, float): 直角坐标系下的横坐标和斜坐标
    """
    x, y = oblique2Cartesian(q, r)
    screen_x = 300 + x * 40
    screen_y = 300 - y * 40
    return screen_x, screen_y


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
    if player == ChineseCheckersApp.Pos.PLAYER1:
        return r in valid_init_oblique_1.get(q, [])
    elif player == ChineseCheckersApp.Pos.PLAYER2:
        return r in valid_init_oblique_2.get(q, [])
    else:
        return False


def create_array_exclude_both(a, b):
    """生成数组[a+1, a+2,..., b-2, b-1]

    Args:
        a (int): 
        b (int): 

    Returns:
        list(int): [a+1, a+2,..., b-2, b-1]
    """
    if a > b:
        a, b = b, a
    return list(range( a + 1 , b))  


'''========================= 跳棋游戏类 ====================================='''

class ChineseCheckersApp:
    class GameMode(Enum):
        """当前游戏模式枚举类"""
        PVP = 0
        PVE = 1
    class Turn(Enum):
        """当前棋局状态枚举类"""
        PLAYER1_TURN = 0
        PLAYER2_TURN = 1
        AI_TURN = -1
    class Pos(Enum):
        """当前落棋点位置状态枚举类"""
        BLANK = 0
        PLAYER1 = 1
        PLAYER2 = -1
        
    """====================== 初始化函数 ================================="""
    def __init__(self, master, game_mode=GameMode.PVE):
        self.color1_ = "red"
        self.color2_ = "blue"
        self.game_mode = game_mode
        self.current_turn = self.Turn.PLAYER1_TURN
        self.selected_pos_ = None
        self.valid_moves = []
        self.valid_paths = []
        self.draw_path = []
        self.need_draw_path = False
        
        self.master = master
        self.master.title("Chinese Checkers")
        self.board = self.create_chinese_checkers_board()
        self.canvas = tk.Canvas(self.master, width=600, height=600)
        self.canvas.pack()
        # 用于指示当前轮次的圆圈
        self.turn_indicator = self.canvas.create_oval(550, 10, 590, 50, fill=self.color1_)
        self.drawBoard()
        self.canvas.bind("<Button-1>", self.handleClick)
        self.q_valid_positions = {
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
        self.r_valid_positions = {
            r: [q for q, rs in self.q_valid_positions.items() if r in rs] \
                for r in range(-8, 9)
        }
        self.data_q_plus_r = {
            k: [(q, k - q) for q in range(-8, 9) if k - q in self.r_valid_positions.get(q, [])] \
                for k in range(-8, 9)
        }

    def create_chinese_checkers_board(self):
        """创建初始棋盘，使用斜坐标系标记点。"""
        board = {}
        for q in range(-8, 9):
            for r in range(-8, 9):
                if not isValidOblique(q, r):
                    continue
                if isValidInitOblique(self.Pos.PLAYER1, q, r):
                    board[(q,r)] = self.Pos.PLAYER1   # 玩家1
                elif isValidInitOblique(self.Pos.PLAYER2, q, r):
                    board[(q,r)] = self.Pos.PLAYER2   # 玩家2
                else:
                    board[(q, r)] = self.Pos.BLANK # 玩家2
        return board

    def drawBoard(self):
        """绘制棋盘"""
        self.canvas.delete("all")
        
        # 重新绘制轮次指示圆圈
        color = self.color1_ if self.current_turn == self.Turn.PLAYER1_TURN else self.color2_
        self.canvas.create_oval(555, 15, 585, 45, fill=color)
        
        # 重新绘制每个落棋点
        for (q, r), value in self.board.items():
            screen_x, screen_y = oblique2Screen(q, r)
            # 绘制落棋点
            color = "white" if value == self.Pos.BLANK \
                else (self.color1_ if value == self.Pos.PLAYER1 else self.color2_)
            self.canvas.create_oval(screen_x - 15, screen_y - 15, screen_x + 15, screen_y + 15, fill=color)
            
            # 绘制选中棋子特殊高亮
            if self.selected_pos_ == (q, r):
                self.canvas.create_oval(screen_x - 5, screen_y - 5, screen_x + 5, screen_y + 5, fill="yellow")
            # 绘制可行点
            elif (q, r) in self.valid_moves:
                color = self.color1_ if self.current_turn == self.Turn.PLAYER1_TURN else self.color2_
                self.canvas.create_rectangle(
                    screen_x - 20, screen_y - 20, screen_x + 20, screen_y + 20,
                    outline=color, width=2, dash=(4, 2)
                )
        # 绘制已走过的路径
        if self.need_draw_path:
            start_drawed = False
            for q, r in self.draw_path:
                screen_x, screen_y = oblique2Screen(q, r)
                if not start_drawed:
                    start_drawed = True      
                else:
                    # 此处颜色相反对应，因为current_turn已经切换了
                    color = self.color2_ if self.current_turn == self.Turn.PLAYER1_TURN else self.color1_
                    self.canvas.create_line(last_screen_x, last_screen_y, screen_x, screen_y, fill=color, width=2, dash=(4, 2))
                last_screen_x = screen_x
                last_screen_y = screen_y
                    
                
    def findValidPos(self, q, r):
        moves = []
        new_board = self.board.copy() # 该字典没有嵌套对象，直接使用浅拷贝复制即可
        if (q,r) != self.selected_pos_:
            new_board[(q,r)] = self.Pos.PLAYER1 if self.current_turn == self.Turn.PLAYER1_TURN \
                else self.Pos.PLAYER2
            new_board[self.selected_pos_] = self.Pos.BLANK
        moves.extend(self.findValidPosDegree_0(new_board, q, r))
        moves.extend(self.findValidPosDegree_60(new_board, q, r))
        moves.extend(self.findValidPosDegree_120(new_board, q, r))
        return moves
    
    def findValidPosDegree_0(self, board, q, r):
        """在(q,r)所在的水平轴线上寻找下一跳可行点，不考虑平移1格

        Args:
            q (int): 当前棋子位置的斜坐标系横坐标
            r (int): 当前棋子位置的斜坐标系纵坐标

        Returns:
            list(tuple(int,int)): 下一跳的可行位置斜坐标列表
        """
        moves_q = []
        
        for temp_q in self.r_valid_positions.get(r,[]):
            is_mid_q_valid_ = True
            is_end_q_valid = True
            
            if temp_q != q:
                # 判断当前temq 是否为合法中间点
                # 中间点不为空
                if board[(temp_q, r)] == self.Pos.BLANK:
                    continue
                else:
                    for dq in create_array_exclude_both(q, temp_q):
                        if board[(dq, r)] != self.Pos.BLANK:
                            is_mid_q_valid_ = False
                            break
                    if not is_mid_q_valid_:
                        continue
                
                # 终点在棋盘可行域上
                is_end_on_blank_board =  ((2*temp_q-q) in self.q_valid_positions.get(r,[]) \
                    and board[(2*temp_q-q, r)] == self.Pos.BLANK)
                if not is_end_on_blank_board:
                    continue
                
                # 终点与中间点之间全为空
                for dq in create_array_exclude_both(temp_q, 2*temp_q-q):
                    if board[(dq, r)] != self.Pos.BLANK:
                        is_end_q_valid = False
                
                if is_end_q_valid:
                    moves_q.append((2*temp_q - q, r))
        
        return moves_q
    
    def findValidPosDegree_60(self, board, q, r):
        """在(q,r)所在的60°轴线上寻找下一跳可行点，不考虑平移1格

        Args:
            q (int): 当前棋子位置的斜坐标系横坐标
            r (int): 当前棋子位置的斜坐标系纵坐标

        Returns:
            list(tuple(int,int)): 下一跳的可行位置斜坐标列表
        """
        moves_r = []

        for temp_r in self.q_valid_positions.get(q, []):
            is_mid_r_valid_ = True
            is_end_r_valid = True
            
            if temp_r != r:
                # 中间点不为空
                if board[(q, temp_r)] == self.Pos.BLANK:
                    continue
                # 起点与中间点之间全为空
                else:
                    for dr in create_array_exclude_both(r, temp_r):
                        if board[(q, dr)] != self.Pos.BLANK:
                            is_mid_r_valid_ = False
                            break
                    if not is_mid_r_valid_:
                        continue
                    
                # 终点在棋盘可行域上
                is_end_on_blank_board =  ((2*temp_r-r) in self.q_valid_positions.get(q, []) \
                    and board[(q, 2*temp_r-r)] == self.Pos.BLANK)
                if not is_end_on_blank_board:
                    continue
                
                # 终点与中间点之间全为空
                for dr in create_array_exclude_both(temp_r, 2*temp_r-r):
                    if board[(q, dr)] != self.Pos.BLANK:
                        is_end_r_valid = False
                if is_end_r_valid:
                    moves_r.append((q, 2*temp_r-r))
        return moves_r
 
    def findValidPosDegree_120(self, board, q, r):
        """在(q,r)所在的120°轴线上寻找下一跳可行点，不考虑平移1格

        Args:
            q (int): 当前棋子位置的斜坐标系横坐标
            r (int): 当前棋子位置的斜坐标系纵坐标

        Returns:
            list(tuple(int,int)): 下一跳的可行位置斜坐标列表
        """
        moves_q_r = []

        for (temp_q, temp_r) in self.data_q_plus_r.get(q + r, []):
            
            is_mid_valid = True
            is_end_valid = True

            if temp_r != r:
                # 中间点不为空
                if board[(temp_q, temp_r)] == self.Pos.BLANK:
                    continue
                # 起点与中间点之间全为空
                else :
                    for dr in create_array_exclude_both(r, temp_r):
                        if board[(q + r - dr, dr)] != self.Pos.BLANK:
                            is_mid_valid = False
                            break
                    if not is_mid_valid:
                        continue
              
                # 终点在棋盘可行域上
                is_end_on_blank_board = ((2*temp_q-q, 2*temp_r-r) in self.data_q_plus_r.get(q + r , []) \
                    and board[(2*temp_q-q, 2*temp_r-r)] == self.Pos.BLANK)
                if not is_end_on_blank_board:
                    continue
                
                # 终点与中间点之间全为空
                for dr in create_array_exclude_both(temp_r, 2*temp_r-r):
                    if board[(q + r - dr , dr)] != self.Pos.BLANK:
                        is_end_valid = False
                if is_end_valid:
                    moves_q_r.append((2*temp_q-q, 2*temp_r-r))
        
        return moves_q_r          

    def getValidMoves(self, q, r):
        """找到(q,r)位置棋子的下一步所有可行点

        Args:
            q (int): 当前棋子位置的斜坐标系横坐标
            r (int): 当前棋子位置的斜坐标系纵坐标

        Returns:
            list(tuple(int,int)): 所有可行点的斜坐标
            list(list(tuple(int,int))): 所有可行的路径
        """
        moves = []
        paths = []  # 记录完整路径

        # 移动一次的简单移动
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, -1), (-1, 1)]
        for dq, dr in directions:
            nq, nr = q + dq, r + dr
            if isValidOblique(nq, nr) and self.board[(nq, nr)] == self.Pos.BLANK:
                moves.append((nq, nr))
                paths.append([(q, r), (nq, nr)])  # 添加路径：从起点到终点

        # 初始化队列，并将起始节点添加到队列中
        queue = deque()
        queue.append([(q, r)])  # 队列中存储路径
        visited = set()
        visited.add((q, r))

        while queue:
            # 取出队列中的第一条路径
            current_path = queue.popleft()
            current_position = current_path[-1]  # 当前路径的末尾是当前位置

            # 扩展路径并将新的路径加入队列
            neighbors = self.findValidPos(*current_position)
            
            for neighbor in neighbors:
                if neighbor not in visited:
                    # 构造新的路径
                    new_path = current_path + [neighbor]
                    queue.append(new_path)
                    visited.add(neighbor)
                    moves.append(neighbor)
                    paths.append(new_path)  # 保存完整路径

        return moves, paths
    

    def movePos(self, begin, end):
        self.board[end] = self.board[begin]
        self.board[begin] = self.Pos.BLANK

    def ai_turn(self):
        # Placeholder for AI logic
        moves = []  # AI logic to find moves here
        if moves:
            start, end = moves[0]
            self.movePos(start, end)
        self.drawBoard()
        self.toggleTurn()
    
    def toggleTurn(self):
        if self.game_mode == self.GameMode.PVE:
            if self.current_turn == self.Turn.PLAYER1_TURN:
                self.current_turn = self.Turn.AI_TURN
            else :
                self.current_turn = self.Turn.PLAYER1_TURN
        else :
            if self.current_turn == self.Turn.PLAYER1_TURN:
                self.current_turn = self.Turn.PLAYER2_TURN
            else :
                self.current_turn = self.Turn.PLAYER1_TURN
                
    def handleClick(self, event):
        """ 处理鼠标左键单击事件 """

        # 若当前是AI回合，屏蔽鼠标点击响应
        if self.current_turn == self.Turn.AI_TURN:
            return

        clicked_x = (event.x - 300) / 40
        clicked_y = (300 - event.y) / 40
        q, r = cartesian2Oblique(clicked_x, clicked_y)

        if self.selected_pos_:
            # 第二次点击
            if (q, r) in self.valid_moves:  # 移动棋子
                self.movePos(self.selected_pos_, (q, r))
                
                # 我需要在这一步记录下来，self.valid_paths中，从self.selected_pos_到(q,r)的路径
                for path in self.valid_paths:
                    if path[-1] == (q,r) :
                        self.need_draw_path = True
                        self.draw_path = path
                        break
                
                self.toggleTurn()
                self.selected_pos_ = None
                self.valid_moves = []
                self.valid_paths = []
            elif self.board[(q, r)] == (self.Pos.PLAYER1 \
                    if self.current_turn == self.Turn.PLAYER1_TURN \
                    else self.Pos.PLAYER2):
                self.selected_pos_ = (q, r) # 更换选中的棋子
                self.valid_moves, self.valid_paths = self.getValidMoves(q, r)
        else:
            # 第一次点击：选择棋子
            if self.board[(q, r)] == (self.Pos.PLAYER1 \
                    if self.current_turn == self.Turn.PLAYER1_TURN \
                    else self.Pos.PLAYER2):
                self.selected_pos_ = (q, r)
                self.need_draw_path = False
                self.draw_path = []
                self.valid_moves, self.valid_paths = self.getValidMoves(q, r)
                
        self.drawBoard()
        
if __name__ == "__main__":
    root = tk.Tk()
    app = ChineseCheckersApp(root, ChineseCheckersApp.GameMode.PVP)
    root.mainloop()

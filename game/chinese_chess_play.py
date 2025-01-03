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



def create_array_between(q1,r1, q2,r2):
    ans = []
    if q1 == q2:
        if r1 > r2:
            r1, r2 = r2, r1
        ans.extend([(q1, r) for r in list(range(r1 + 1, r2))])
    elif r1 == r2:
        if q1 > q2:
            q1, q2 = q2, q1
        ans.extend([(q, r1) for q in list(range(q1 + 1, q2))])
    elif q1 + r1 == q2 + r2:
        sum = q1 + r1
        if r1 > r2:
            r1, r2 = r2, r1
        ans.extend([(sum - r, r) for r in list(range(r1 + 1, r2))])
    else:
        raise ValueError("The two positions are not on a line.")
    return ans 


'''========================= 跳棋游戏类 ====================================='''

class ChineseCheckersApp:
    class PlayerNum(Enum):
        """当前玩家数量枚举类"""
        FOR2PLAYER = 2
        FOR3PLAYER = 3
        FOR4PLAYER = 4
        FOR6PLAYER = 6
    class GameMode(Enum):
        """当前游戏模式枚举类"""
        PVP = 0
        PVE = 1
        
    """====================== 初始化函数 ================================="""
    def __init__(self, master, player_num, game_mode=GameMode.PVP, ai_list = []):
        '''==================== 配置参数, 常量 ===================='''
        self.player_dict = {
            self.PlayerNum.FOR2PLAYER: [1, 4],
            self.PlayerNum.FOR3PLAYER: [1, 3, 5],
            self.PlayerNum.FOR4PLAYER: [2, 3, 5, 6],
            self.PlayerNum.FOR6PLAYER: [1, 2, 3, 4, 5, 6] 
        }
        self.player_colors = ["white", "red", "#FF8C00", "magenta", "green", "blue", "purple"]
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
        self.q_plus_r_valid_pos = {
            k: [(q, k - q) for q in range(-8, 9) if k - q in self.r_valid_positions.get(q, [])] \
                for k in range(-8, 9)
        }
        self.home_pos = {
            1: [(1, -5), (2, -6), (2, -5), (3, -7), (3, -6), (3, -5), \
                (4, -8), (4, -7), (4, -6), (4, -5)],
            2: [(5, -4), (5, -3), (5, -2), (5, -1), (6, -4), (6, -3), \
                (6, -2), (7, -4), (7, -3), (8, -4)],
            3: [(1, 4), (2, 3), (2, 4), (3, 2), (3, 3), (3, 4), \
                (4, 1), (4, 2), (4, 3), (4, 4)],
            4: [(-4, 5), (-4, 6), (-4, 7), (-4, 8), (-3, 5), (-3, 6), \
                (-3, 7), (-2, 5), (-2, 6), (-1, 5)],
            5: [(-8, 4), (-7, 3), (-7, 4), (-6, 2), (-6, 3), (-6, 4), \
                (-5, 1), (-5, 2), (-5, 3), (-5, 4)],
            6: [(-4, -4), (-4, -3), (-4, -2), (-4, -1), (-3, -4), (-3, -3), \
                (-3, -2), (-2, -4), (-2, -3), (-1, -4)]
        }
        self.base_pos = {
            1: (4, -8),
            2: (8, -4),
            3: (4, 4),
            4: (-4, 8),
            5: (-8, 4),
            6: (-4, -4)
        }
        '''==================== 变量初始化，与外部输入无关 ===================='''
        self.selected_pos = None
        self.valid_moves = []
        self.valid_paths = []
        self.draw_path = []
        self.need_draw_path = False
        self.last_turn = None
        self.player_ok = False
        self.ai_ok = False
        self.winner = None
        self.game_over = False
        '''==================== 变量初始化，与外部输入有关 ===================='''
        self.player_num = player_num
        self.game_mode = game_mode
        if self.game_mode == self.GameMode.PVE:
            for ai in ai_list:
                if ai not in self.player_dict[self.player_num]:
                    raise ValueError("AI player number is not valid.")
            self.ai_list = ai_list
        else:
            self.ai_list = []
        self.current_turn = self.player_dict[self.player_num][0]
        self.master = master
        self.master.title("Chinese Checkers")
        self.canvas = tk.Canvas(self.master, width=600, height=600)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.handleClick)
        self.board = self.create_chinese_checkers_board()
    # 检查斜坐标是否合法
    def isValidOblique(self, q, r):
        """检查给定的斜坐标是否是合法的棋盘点。"""    
        return r in self.q_valid_positions.get(q, [])

    def isValidInitOblique(self, player, q, r):
        return (q, r) in self.home_pos.get(player, [])
    def create_ai_list(self):
        """创建AI列表"""
        ai_list = []
        for i in range(1, self.player_num + 1):
            if i not in self.player_dict[self.player_num]:
                ai_list.append(i)
        return ai_list
    def create_chinese_checkers_board(self):
        """创建初始棋盘，使用斜坐标系标记点。"""
        board = {}
        for q in range(-8, 9):
            for r in self.q_valid_positions.get(q, []):
                is_created = False
                for i in self.player_dict[self.player_num]:
                    if self.isValidInitOblique(i, q, r):
                        board[(q,r)] = i
                        is_created = True
                        break
                if not is_created:
                    board[(q,r)] = 0
        return board

    def drawBoard(self):
        """绘制棋盘"""
        self.canvas.delete("all")
        
        # 重新绘制轮次指示圆圈
        color = self.player_colors[self.current_turn]
        self.canvas.create_oval(555, 15, 585, 45, fill=color)
        
        # 重新绘制每个落棋点
        for (q, r), value in self.board.items():
            screen_x, screen_y = oblique2Screen(q, r)
            # 绘制落棋点
            color = self.player_colors[value]
            self.canvas.create_oval(screen_x - 15, screen_y - 15, screen_x + 15, screen_y + 15, fill=color)
            
            # 绘制选中棋子特殊高亮
            if self.selected_pos == (q, r):
                self.canvas.create_oval(screen_x - 5, screen_y - 5, screen_x + 5, screen_y + 5, fill="black")
            # 绘制可行点
            elif (q, r) in self.valid_moves:
                color = self.player_colors[self.current_turn]
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
                    # 此处颜色为上一个回合玩家的颜色，因为current_turn已经切换了
                    color = self.player_colors[self.last_turn]
                    self.canvas.create_line(last_screen_x, last_screen_y, screen_x, screen_y, fill=color, width=2, dash=(4, 2))
                    if (q,r) != self.draw_path[-1]:
                        self.canvas.create_oval(screen_x - 5, screen_y - 5, screen_x + 5, screen_y + 5, fill=color)
                last_screen_x = screen_x
                last_screen_y = screen_y
                                
    def findValidPos(self, in_board, q, r):
        moves = []
        # 构建selected_pos移动到(q,r)之后的棋盘
        board = in_board.copy() # 该字典没有嵌套对象，直接使用浅拷贝复制即可
        if (q,r) != self.selected_pos:
            board[(q,r)] = self.current_turn
            board[self.selected_pos] = 0
            
        possible_mid = []
        possible_mid.extend([(q, psb_r) for psb_r in self.q_valid_positions.get(q, []) \
            if psb_r != r and board[(q, psb_r)] != 0])
        possible_mid.extend([(psb_q, r) for psb_q in self.r_valid_positions.get(r, []) \
            if psb_q != q and board[(psb_q, r)] != 0])
        possible_mid.extend([(psb_q, psb_r) for (psb_q, psb_r) in self.q_plus_r_valid_pos.get(q+r, []) \
            if psb_q != q and board[psb_q, psb_r] != 0])
        
        for (temp_q, temp_r) in possible_mid:
            # 当(temp_q, temp_r)可能是跳板时：
            is_mid_valid = True
            is_end_valid = True
            # 判断(q,r)和(temp_q, temp_r)之间是否全空
            for (mid_q, mid_r) in create_array_between(q, r, temp_q, temp_r):
                if board[(mid_q, mid_r)] != 0:
                    is_mid_valid = False
                    break
            # 判断(2*temp_q-q, 2*temp_r-r)是不是可行点
            if (not is_mid_valid) or (not self.isValidOblique(2*temp_q-q, 2*temp_r-r)) \
                or board[(2*temp_q-q, 2*temp_r-r)] != 0:
                continue
            # 判断(temp_q, temp_r)和(2*temp_q-q, 2*temp_r-r)之间是否全空
            for (mid_q, mid_r) in create_array_between(temp_q, temp_r, 2*temp_q-q, 2*temp_r-r):
                if board[(mid_q, mid_r)] != 0:
                    is_end_valid = False
                    break
            if is_end_valid:
                moves.append((2*temp_q-q, 2*temp_r-r))
        return moves
            

    def getValidMoves(self, board, q, r):
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
            if self.isValidOblique(nq, nr) and board[(nq, nr)] == 0:
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
            neighbors = self.findValidPos(board, *current_position)
            
            for neighbor in neighbors:
                if neighbor not in visited:
                    # 构造新的路径
                    new_path = current_path + [neighbor]
                    queue.append(new_path)
                    visited.add(neighbor)
                    moves.append(neighbor)
                    paths.append(new_path)  # 保存完整路径

        return moves, paths
    

    def movePos(self, board, begin, end):
        board[end] = board[begin]
        board[begin] = 0
        return board
        
    def toggleTurn(self, current_turn):
        last_turn = current_turn
        player_list = self.player_dict.get(self.player_num, [])
        index = player_list.index(current_turn)
        if index == len(player_list) - 1:
            next_turn = player_list[0]
        else:
            next_turn = player_list[index + 1]
        return last_turn, next_turn
                
    def handleClick(self, event):
        """ 处理鼠标左键单击事件 """

        # 若当前是 PVE 模式 AI 回合，屏蔽鼠标点击响应
        if self.game_mode == self.GameMode.PVE and self.current_turn in self.ai_list:
            return

        clicked_x = (event.x - 300) / 40
        clicked_y = (300 - event.y) / 40
        q, r = cartesian2Oblique(clicked_x, clicked_y)
        if not self.isValidOblique(q, r):  # 点击位置不在棋盘上
            return
        
        if self.selected_pos:
            # 第二次点击
            if (q, r) in self.valid_moves:  # 移动棋子
                self.board = self.movePos(self.board, self.selected_pos, (q, r))
            
                for path in self.valid_paths:
                    if path[-1] == (q,r) :
                        self.need_draw_path = True
                        self.draw_path = path
                        break
                
                self.player_ok = True
                self.selected_pos = None
                self.valid_moves = []
                self.valid_paths = []
            elif self.board[(q, r)] == self.current_turn:
                self.selected_pos = (q, r) # 更换选中的棋子
                print(self.selected_pos)
                self.valid_moves, self.valid_paths = self.getValidMoves(self.board, q, r)
        elif self.board[(q, r)] == self.current_turn:
            # 第一次点击：选择棋子   
                self.selected_pos = (q, r)
                print(self.selected_pos)
                self.need_draw_path = False
                self.draw_path = []
                self.valid_moves, self.valid_paths = self.getValidMoves(self.board, q, r)
                
    def checkWinner(self, board):
        """根据棋盘判定游戏是否结束，并给出赢家，工具函数，供外部使用"""
        game_over = False
        winner = None
        for player in self.player_dict.get(self.player_num, []):
            is_player_win = True
            goal = (player + 2) % 6 + 1
            for (q, r) in self.home_pos.get(goal, []):
                if board[(q,r)] != player:
                    is_player_win = False
                    break
            if is_player_win:
                winner = player
                game_over = True
                break
        return game_over, winner
    
    def getScore(self, board, begin, move, player):
        goal = (player + 2) % 6 + 1
       
        goal_q, goal_r = self.base_pos.get(goal)
        base_q, base_r = self.base_pos.get(player)
        
        goal_x, goal_y = oblique2Cartesian(goal_q, goal_r)
        base_x, base_y = oblique2Cartesian(base_q, base_r)
        
        move_x, move_y = oblique2Cartesian(move[0], move[1])
        begin_x, begin_y = oblique2Cartesian(begin[0], begin[1])
        
        return (move_x-begin_x)*(goal_x - base_x) + (move_y-begin_y)*(goal_y-base_y) \
            + 10 * (math.sqrt((begin_x - goal_x)**2 + (begin_y - goal_y)**2) - math.sqrt((move_x - goal_x)**2 + (move_y - goal_y)**2))
    
    
    def play(self):
        # print("chess is running...")
        if self.game_mode == self.GameMode.PVE and self.current_turn in self.ai_list:
            if self.ai_ok:
                self.ai_ok = False
                self.last_turn, self.current_turn = self.toggleTurn(self.current_turn)
        else:
            if self.player_ok:
                self.player_ok = False
                self.last_turn, self.current_turn = self.toggleTurn(self.current_turn)
        self.game_over, self.winner = self.checkWinner(self.board)
        self.drawBoard()
        if not self.game_over:
            self.master.after(1, self.play) 
        else:
            print(f"!!!!!!!!!!!!!!Winner is {self.winner}!!!!!!!!!!!!!!")
    
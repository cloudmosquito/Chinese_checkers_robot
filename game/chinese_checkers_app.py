import math
from enum import Enum
from collections import deque
from mcts_agent import MCTSAgent

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
    class LastPath:
        """绘制路径类"""
        def __init__(self, need_draw, path, player):
            self.need_draw = need_draw
            self.path = path
            self.player = player
        
    """====================== 初始化函数 ================================="""
    def __init__(self, master, player_num, game_mode=GameMode.PVP, ai_list = []):
        '''==================== 配置参数, 常量 ===================='''
        self.player_dict = {
            self.PlayerNum.FOR2PLAYER: [1, 4],
            self.PlayerNum.FOR3PLAYER: [1, 3, 5],
            self.PlayerNum.FOR4PLAYER: [2, 3, 5, 6],
            self.PlayerNum.FOR6PLAYER: [1, 2, 3, 4, 5, 6] 
        }
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
        self.real_board = {(-8, 4): (296.7, -152.7), (-7, 3): (312.8, -144.3), (-7, 4): (297.2, -134.3), (-6, 2): (328.9, -135.9), (-6, 3): (313.3, -125.9), (-6, 4): (297.7, -115.9), (-5, 1): (345.0, -127.5), (-5, 2): (329.4, -117.5), (-5, 3): (313.8, -107.5), (-5, 4): (298.2, -97.5), (-4, -4): (423.3, -159.1), (-4, -3): (407.7, -149.1), (-4, -2): (392.2, -139.1), (-4, -1): (376.6, -129.1), (-4, 0): (361.1, -119.1), (-4, 1): (345.5, -109.1), (-4, 2): (329.9, -99.1), (-4, 3): (314.2, -89.1), (-4, 4): (298.6, -79.1), (-4, 5): (283.0, -69.0), (-4, 6): (267.3, -59.0), (-4, 7): (251.7, -48.9), (-4, 8): (236.0, -38.9), (-3, -4): (423.8, -140.8), (-3, -3): (408.2, -130.8), (-3, -2): (392.7, -120.8), (-3, -1): (377.1, -110.8), (-3, 0): (361.6, -100.8), (-3, 1): (346.0, -90.7), (-3, 2): (330.4, -80.7), (-3, 3): (314.8, -70.7), (-3, 4): (299.2, -60.8), (-3, 5): (283.6, -50.8), (-3, 6): (267.9, -40.7), (-3, 7): (252.3, -30.7), (-2, -4): (424.3, -122.4), (-2, -3): (408.7, -112.5), (-2, -2): (393.2, -102.5), (-2, -1): (377.7, -92.4), (-2, 0): (362.1, -82.4), (-2, 1): (346.5, -72.3), (-2, 2): (330.9, -62.3), (-2, 3): (315.4, -52.4), (-2, 4): (299.9, -42.5), (-2, 5): (284.2, -32.5), (-2, 6): (268.5, -22.4), (-1, -4): (424.8, -104.1), (-1, -3): (409.2, -94.1), (-1, -2): (393.7, -84.1), (-1, -1): (378.2, -74.0), (-1, 0): (362.7, -64.0), (-1, 1): (347.1, -54.0), (-1, 2): (331.5, -44.1), (-1, 3): (316.0, -34.1), (-1, 4): (300.5, -24.2), (-1, 5): (284.8, -14.2), (0, -4): (425.3, -85.8), (0, -3): (409.8, -75.8), (0, -2): (394.2, -65.7), (0, -1): (378.7, -55.6), (0, 0): (363.2, -45.6), (0, 1): (347.7, -35.7), (0, 2): (332.1, -25.8), (0, 3): (316.6, -15.9), (0, 4): (301.1, -6.0), (1, -5): (441.3, -77.5), (1, -4): (425.9, -67.4), (1, -3): (410.4, -57.3), (1, -2): (394.9, -47.3), (1, -1): (379.3, -37.2), (1, 0): (363.9, -27.3), (1, 1): (348.4, -17.4), (1, 2): (332.8, -7.5), (1, 3): (317.3, 2.4), (1, 4): (301.8, 12.2), (2, -6): (457.3, -69.2), (2, -5): (441.9, -59.1), (2, -4): (426.5, -49.0), (2, -3): (411.0, -38.9), (2, -2): (395.5, -28.9), (2, -1): (380.0, -18.9), (2, 0): (364.6, -9.0), (2, 1): (349.1, 0.9), (2, 2): (333.5, 10.9), (2, 3): (318.1, 20.6), (2, 4): (302.6, 30.3), (3, -7): (473.4, -61.0), (3, -6): (458.0, -50.8), (3, -5): (442.6, -40.7), (3, -4): (427.1, -30.5), (3, -3): (411.6, -20.5), (3, -2): (396.2, -10.5), (3, -1): (380.7, -0.6), (3, 0): (365.3, 9.4), (3, 1): (349.8, 19.3), (3, 2): (334.3, 29.0), (3, 3): (318.8, 38.7), (3, 4): (303.4, 48.5), (4, -8): (489.4, -52.7), (4, -7): (474.0, -42.6), (4, -6): (458.6, -32.4), (4, -5): (443.2, -22.2), (4, -4): (427.8, -12.1), (4, -3): (412.3, -2.2), (4, -2): (396.9, 7.8), (4, -1): (381.4, 17.7), (4, 0): (366.0, 27.7), (4, 1): (350.5, 37.4), (4, 2): (335.1, 47.1), (4, 3): (319.6, 56.9), (4, 4): (304.1, 66.6), (5, -4): (428.5, 6.4), (5, -3): (413.1, 16.4), (5, -2): (397.6, 26.3), (5, -1): (382.2, 36.2), (6, -4): (429.2, 25.0), (6, -3): (413.8, 34.9), (6, -2): (398.4, 44.8), (7, -4): (430.0, 43.5), (7, -3): (414.5, 53.4), (8, -4): (430.7, 62.0)}
        '''==================== 变量初始化，与外部输入无关 ===================='''
        self.selected_pos = None
        self.valid_moves = []
        self.valid_paths = []
        self.last_path = self.LastPath(False, [], "white")
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
        self.current_player = self.player_dict[self.player_num][0]
        self.master = master
        
        self.board = self.create_chinese_checkers_board()
    
    """===================== 工具方法 ====================="""

    # 检查斜坐标是否合法
    def isValidOblique(self, q, r):
        """检查给定的斜坐标是否是合法的棋盘点。"""    
        return r in self.q_valid_positions.get(q, [])

    def isValidInitOblique(self, player, q, r):
        return (q, r) in self.home_pos.get(player, [])
    def getPlayerList(self):
        return self.player_dict[self.player_num]
    
    def create_ai_list(self):
        """创建AI列表"""
        ai_list = []
        for i in range(1, self.player_num + 1):
            if i not in self.getPlayerList():
                ai_list.append(i)
        return ai_list
    def create_chinese_checkers_board(self):
        """创建初始棋盘，使用斜坐标系标记点。"""
        board = {}
        for q in range(-8, 9):
            for r in self.q_valid_positions.get(q, []):
                is_created = False
                for i in self.getPlayerList():
                    if self.isValidInitOblique(i, q, r):
                        board[(q,r)] = i
                        is_created = True
                        break
                if not is_created:
                    board[(q,r)] = 0
        return board
                           
    def findValidPos(self, in_board, q, r):
        moves = []
        # 构建selected_pos移动到(q,r)之后的棋盘
        board = in_board.copy() # 该字典没有嵌套对象，直接使用浅拷贝复制即可
        if (q,r) != self.selected_pos:
            board[(q,r)] = self.current_player
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
        
    def switchTurn(self, current_player):
        player_list = self.getPlayerList()
        index = player_list.index(current_player)
        if index == len(player_list) - 1:
            next_player = player_list[0]
        else:
            next_player = player_list[index + 1]
        return next_player
                
    def playerSelect(self, selected_q, selected_r, is_ai):
        if not is_ai and self.game_mode == self.GameMode.PVE and self.current_player in self.ai_list:
            return

        if not self.isValidOblique(selected_q, selected_r):  # 点击位置不在棋盘上
            return
        
        if self.selected_pos:
            # 第二次点击
            if (selected_q, selected_r) in self.valid_moves:  # 移动棋子
                self.board = self.movePos(self.board, self.selected_pos, (selected_q, selected_r))
            
                for path in self.valid_paths:
                    if path[-1] == (selected_q,selected_r) :
                        self.last_path.need_draw = True
                        self.last_path.path = path
                        self.last_path.player = self.current_player
                        break
                if not is_ai:
                    self.player_ok = True
                self.selected_pos = None
                self.valid_moves = []
                self.valid_paths = []
            elif self.board[(selected_q, selected_r)] == self.current_player:
                self.selected_pos = (selected_q, selected_r) # 更换选中的棋子
                self.valid_moves, self.valid_paths = self.getValidMoves(self.board, selected_q, selected_r)
        elif self.board[(selected_q, selected_r)] == self.current_player:
            # 第一次点击：选择棋子   
                self.selected_pos = (selected_q, selected_r)
                self.last_path.need_draw = False
                self.valid_moves, self.valid_paths = self.getValidMoves(self.board, selected_q, selected_r)
                
    def checkWinner(self, board):
        """根据棋盘判定游戏是否结束，并给出赢家，工具函数，供外部使用"""
        game_over = False
        winner = None
        for player in self.getPlayerList():
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
    
    def getScoreMove(self, board, begin, move, player):
        goal = (player + 2) % 6 + 1
       
        goal_q, goal_r = self.base_pos.get(goal)
        base_q, base_r = self.base_pos.get(player)
        
        goal_x, goal_y = oblique2Cartesian(goal_q, goal_r)
        base_x, base_y = oblique2Cartesian(base_q, base_r)
        
        move_x, move_y = oblique2Cartesian(move[0], move[1])
        begin_x, begin_y = oblique2Cartesian(begin[0], begin[1])
        
        return (move_x-begin_x)*(goal_x - base_x) + (move_y-begin_y)*(goal_y-base_y) \
            + 10 * (math.sqrt((begin_x - goal_x)**2 + (begin_y - goal_y)**2) - math.sqrt((move_x - goal_x)**2 + (move_y - goal_y)**2))
    
    def getScoreBoard(self, board, player):
        score = 0
        goal = (player + 2) % 6 + 1
        for pos in self.home_pos.get(goal, []):
            if self.board[pos] == player:
                score += 10
        for pos in self.home_pos.get(player, []):
            if self.board[pos] == player:
                score -= 5
        return score
                
    
    def play(self):
        # print("chess is running...")
        if self.game_mode == self.GameMode.PVE and self.current_player in self.ai_list:
            if self.ai_ok:
                self.ai_ok = False
                self.current_player = self.switchTurn(self.current_player)
        else:
            if self.player_ok:
                self.player_ok = False
                self.current_player = self.switchTurn(self.current_player)
        self.game_over, self.winner = self.checkWinner(self.board)
        if not self.game_over:
            self.master.after(1, self.play) 
        else:
            print(f"!!!!!!!!!!!!!!  Winner is {self.winner}  !!!!!!!!!!!!!!")



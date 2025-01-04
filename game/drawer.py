from chinese_checkers_app import oblique2Cartesian

class Drawer:
    def __init__(self, master, canvas, app):
        self.player_colors = ["white", "red", "#FF8C00", "magenta", "green", "blue", "purple"]
        self.master = master
        self.canvas = canvas
        self.app = app
    """===============================工具方法======================================"""
    def oblique2Screen(self, q, r):
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
    
    def getCurrentColor(self):
        return self.player_colors[self.app.current_player]
    
    def getPlayerColor(self, player):
        return self.player_colors[player]
    """================================主要工作方法===================================="""
    def drawBoard(self):
        """绘制棋盘"""
        self.canvas.delete("all")
        
        # 重新绘制轮次指示圆圈
        current_color = self.player_colors[self.app.current_player]
        self.canvas.create_oval(555, 15, 585, 45, fill=current_color)
        
        # 重新绘制每个落棋点
        for (q, r), player in self.app.board.items():
            screen_x, screen_y = self.oblique2Screen(q, r)
            # 绘制落棋点
            color = self.player_colors[player]
            self.canvas.create_oval(screen_x - 15, screen_y - 15, screen_x + 15, screen_y + 15, fill=color)
        # 绘制选中点
        if self.app.selected_pos is not None:
            selected_x, selected_y = self.oblique2Screen(self.app.selected_pos[0], self.app.selected_pos[1])
            self.canvas.create_oval(selected_x - 5, selected_y - 5, selected_x + 5, selected_y + 5, fill="black")    
        # 绘制可行点
        for (q,r) in self.app.valid_moves:
            screen_x, screen_y = self.oblique2Screen(q, r)
            self.canvas.create_rectangle(
                screen_x - 20, screen_y - 20, screen_x + 20, screen_y + 20,
                outline=current_color, width=2, dash=(4, 2)
            )        
        # 绘制已走过的路径
        if self.app.last_path.need_draw:
            start_drawed = False
            last_screen_x = last_screen_y = 0
            for q, r in self.app.last_path.path:
                screen_x, screen_y = self.oblique2Screen(q, r)
                if not start_drawed:
                    start_drawed = True      
                else:
                    color = self.player_colors[self.app.last_path.player]
                    self.canvas.create_line(last_screen_x, last_screen_y, screen_x, screen_y, fill=color, width=2, dash=(4, 2))
                    if (q,r) != self.app.last_path.path[-1]:
                        self.canvas.create_oval(screen_x - 5, screen_y - 5, screen_x + 5, screen_y + 5, fill=color)
                last_screen_x = screen_x
                last_screen_y = screen_y
        if not self.app.game_over:
            self.master.after(1, self.drawBoard) 
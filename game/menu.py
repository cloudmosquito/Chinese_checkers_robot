import tkinter as tk
from tkinter import messagebox
import pyttsx3
from mcts_agent import MCTSAgent
import threading
from chinese_checkers_app import ChineseCheckersApp as App
from chinese_checkers_app import cartesian2Oblique
from comm import comm
from drawer import Drawer

class MainMenu:
    def __init__(self, master, sk, is_playing_simulation):
        self.master = master
        self.master.title("Chinese Checkers")
        self.master.geometry("400x600")
        self.engine = pyttsx3.init()
        self.sk = sk
        self.is_playing_simulation = is_playing_simulation
        self.start_button = tk.Button(master, text="开始游戏", command=self.select_game_mode, bg="red", fg="white", width=20, height=3)
        self.start_button.pack(pady=60)
        
        self.instructions_button = tk.Button(master, text="游戏说明", command=self.show_instructions, bg="blue", fg="white", width=20, height=3)
        self.instructions_button.pack(pady=60)
        
        self.exit_button = tk.Button(master, text="退出游戏", command=self.exit_game, bg="gray", fg="white", width=20, height=3)
        self.exit_button.pack(pady=60)

    def speak(self, text):
        """使用 pyttsx3 播放语音"""
        self.engine.say(text)
        self.engine.runAndWait()

    def select_game_mode(self):
        """让玩家选择游戏模式：人机对战或玩家对战。"""
        self.master.withdraw()  # 隐藏主界面
        mode_window = tk.Toplevel(self.master)
        mode_window.title("选择游戏模式")
        mode_window.geometry("300x300")
        
        tk.Label(mode_window, text="请选择游戏模式：", font=("Arial", 14)).pack(pady=20)
        tk.Button(mode_window, text="玩家对战", bg="red", fg="white",
                  command=lambda: self.start_game(mode_window, App.PlayerNum.FOR2PLAYER, App.GameMode.PVP),
                  width=20, height=2).pack(pady=10)
        tk.Button(mode_window, text="人机对战", bg="blue", fg="white",
                  command=lambda: self.select_ai_difficulty(mode_window), width=20, height=2).pack(pady=30)
        
        # 延迟语音提示，确保界面加载完成后播放
        mode_window.after(500, lambda: self.speak("请选择游戏模式"))

    def select_ai_difficulty(self, parent_window):
        """选择 AI 的难度级别。"""
        parent_window.destroy()
        difficulty_window = tk.Toplevel(self.master)
        difficulty_window.title("选择AI难度")
        difficulty_window.geometry("300x300")

        tk.Label(difficulty_window, text="请选择AI难度：", font=("Arial", 14)).pack(pady=20)
        tk.Button(difficulty_window, text="简单", bg="red", fg="white",
                  command=lambda: self.start_game(difficulty_window, App.PlayerNum.FOR2PLAYER, App.GameMode.PVE, [4]),
                  width=20, height=2).pack(pady=10)
        tk.Button(difficulty_window, text="中等", bg="blue", fg="white",
                  command=lambda: self.start_game(difficulty_window, App.PlayerNum.FOR2PLAYER, App.GameMode.PVE, [4]),
                  width=20, height=2).pack(pady=10)
        tk.Button(difficulty_window, text="困难", bg="green", fg="white",
                  command=lambda: self.start_game(difficulty_window, App.PlayerNum.FOR2PLAYER, App.GameMode.PVE, [4]),
                  width=20, height=2).pack(pady=10)

        # 延迟语音提示
        difficulty_window.after(500, lambda: self.speak("请选择难度"))
    def show_instructions(self):
        rules = """
        跳棋规则：
        1. 玩家轮流移动棋子。
        2. 棋子可以移动到相邻的空格或跳过一颗棋子。
        3. 首先将所有棋子移动到对面基地者胜。
        """
        messagebox.showinfo("游戏说明", rules)
        self.master.after(500, lambda: self.speak(rules.strip()))

    def exit_game(self):
        """弹出确认退出窗口"""
        exit_window = tk.Toplevel(self.master)
        exit_window.title("退出游戏")
        exit_window.geometry("300x200")
        tk.Label(exit_window, text="真的要退出吗？", font=("Arial", 12)).pack(pady=10)
        tk.Button(exit_window, text="确认", command=self.master.quit, bg="red", fg="white", width=10).pack(side="left", padx=20)
        tk.Button(exit_window, text="取消", command=exit_window.destroy, bg="green", fg="white", width=10).pack(side="right", padx=20)
        exit_window.after(500, lambda: self.speak("真的要退出吗"))
    
    def handleClick(self, event):
        clicked_x = (event.x - 300) / 40
        clicked_y = (300 - event.y) / 40
        q,r = cartesian2Oblique(clicked_x, clicked_y)
        self.app.playerSelect(q, r, is_ai=False)
    
    def start_game(self, parent_window, player_num, game_mode, ai_list=[]):
        """启动游戏窗口，并设置游戏模式和玩家数量。"""
        parent_window.destroy()
        game_window = tk.Toplevel(self.master)
        game_window.title("游戏界面")
        self.speak("游戏开始")
        canvas = tk.Canvas(game_window, width=600, height=600)
        canvas.pack()
        canvas.bind("<Button-1>", self.handleClick)
        self.app = App(game_window, player_num=player_num, game_mode=game_mode, ai_list=ai_list)
        drawer = Drawer(game_window, canvas, self.app)
        drawer.drawBoard()
        self.app.play()
        if ai_list:
          for ai in ai_list:
            ai_player = MCTSAgent(self.app, ai, self.is_playing_simulation)
            threading.Thread(target=ai_player.run, daemon=True).start()
            if not self.is_playing_simulation:
              robot_comm = comm(ai_player, self.app, self.sk)
              threading.Thread(target=robot_comm.act, daemon=True).start()
        
  
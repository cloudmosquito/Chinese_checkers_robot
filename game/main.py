from chinese_chess_play import ChineseCheckersApp
from mcts_agent import MCTSAgent
import tkinter as tk
import threading

root = tk.Tk()
app = ChineseCheckersApp(root, ChineseCheckersApp.PlayerNum.FOR3PLAYER, ChineseCheckersApp.GameMode.PVE, [3, 5])
ai_player1 = MCTSAgent(app, 3)
ai_player2 = MCTSAgent(app, 5)
app.play()
threading.Thread(target=ai_player1.run, daemon=True).start()
threading.Thread(target=ai_player2.run, daemon=True).start()
root.mainloop()
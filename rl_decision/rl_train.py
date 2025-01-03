import tkinter as tk
from rl_env import CheckersEnv
from rl_agent_dqn import DQNAgent
import sys
sys.path.append('E:\\OriginalF\\Undergraduate\\automatition_practice\\Chinese_chess_robot')
from game.chinese_chess_play import ChineseCheckersApp

root = tk.Tk()
app = ChineseCheckersApp(root, ChineseCheckersApp.PlayerNum.FOR2PLAYER, ChineseCheckersApp.GameMode.PVE, [1, 4])
env = CheckersEnv(app)
state_dim = env.get_state().shape[0]
action_dim = 300  # 假设最多300种动作
agent = DQNAgent(state_dim, action_dim, 1)

for episode in range(1000):
    state = env.reset()
    total_reward = 0
    done = False

    while not done:
        action = agent.choose_action(state)
        next_state, reward, done = env.step(action)
        agent.store_experience(state, action, reward, next_state, done)
        agent.train()
        state = next_state
        total_reward += reward

    print(f"Episode {episode}, Total Reward: {total_reward}")

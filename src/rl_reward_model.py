import torch  #  导入PyTorch库，主模块
import torch.nn as nn #  导入PyTorch库，神经网络模块
import torch.optim as optim #  导入PyTorch库，优化算法

class RewardModel(nn.Module): # 继承nn.Module神经网络模块
    def __init__(self, state_dim):
        super(RewardModel, self).__init__() # 调用父类的构造函数
        self.fc1 = nn.Linear(state_dim, 128) # 输入层，全连接层，输入维度为state_dim，输出维度为128
        self.fc2 = nn.Linear(128, 128) # 隐藏层，全连接层，输入维度为128，输出维度为128
        self.fc3 = nn.Linear(128, 1)  # 输出一个标量表示奖励

    def forward(self, state):
        x = torch.relu(self.fc1(state))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)
      
      
def self_play(env, agent, reward_model, num_episodes=100):
    """
    进行自我对弈，生成状态和对局结果数据。
    """
    data = []
    for _ in range(num_episodes):
        state = env.reset()
        done = False
        trajectory = []

        while not done:
            action = agent.select_action(state)  # 选择动作
            next_state, _, done = env.step(action)
            trajectory.append((state, action))  # 保存轨迹
            state = next_state

        # 根据最终结果计算每个状态的奖励
        winner = env.get_winner()  # 获取胜者
        reward = 1 if winner == agent.player_id else -1

        for s, a in trajectory:
            data.append((s, a, reward))  # 将结果与状态相关联

    return data

def train_reward_function(reward_model, data, lr=0.001, epochs=10):
    """
    使用对弈数据训练奖励函数。
    """
    optimizer = optim.Adam(reward_model.parameters(), lr=lr)
    loss_fn = nn.MSELoss()

    for epoch in range(epochs):
        total_loss = 0
        for state, action, true_reward in data:
            state = torch.FloatTensor(state).unsqueeze(0)  # 添加批次维度
            predicted_reward = reward_model(state)

            # 计算损失
            loss = loss_fn(predicted_reward, torch.tensor([[true_reward]]))
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        print(f"Epoch {epoch + 1}, Loss: {total_loss:.4f}")


# 初始化环境、策略网络和奖励模型
env = ChineseCheckersEnv()
reward_model = RewardModel(state_dim=128)
agent = DQNAgent(state_dim=128, action_dim=64)  # 假设 64 种可能动作

# 自我对弈和迭代训练
for iteration in range(10):
    print(f"Iteration {iteration + 1}")

    # 1. 自我对弈生成数据
    data = self_play(env, agent, reward_model)

    # 2. 训练奖励模型
    train_reward_function(reward_model, data)

    # 3. 更新策略网络
    agent.train_with_reward_model(env, reward_model)

    # 评估表现
    evaluate_agent(env, agent)


import numpy as np
import random

class DQNAgent:
    def __init__(self, state_dim, action_dim):
        self.model = DQN(state_dim, action_dim)  # 策略网络
        self.target_model = DQN(state_dim, action_dim)  # 目标网络
        self.target_model.load_state_dict(self.model.state_dict())
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        self.memory = ReplayBuffer(10000)
        self.gamma = 0.99  # 折扣因子
        self.epsilon = 1.0  # 初始探索概率
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.1

    def select_action(self, state):
        if np.random.rand() < self.epsilon:
            return random.choice(range(action_dim))
        state = torch.FloatTensor(state).unsqueeze(0)
        q_values = self.model(state)
        return torch.argmax(q_values).item()

    def train_step(self, batch_size):
        if len(self.memory) < batch_size:
            return
        batch = self.memory.sample(batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)

        states = torch.FloatTensor(states)
        actions = torch.LongTensor(actions).unsqueeze(1)
        rewards = torch.FloatTensor(rewards)
        next_states = torch.FloatTensor(next_states)
        dones = torch.FloatTensor(dones)

        # 计算目标Q值
        q_targets = rewards + self.gamma * self.target_model(next_states).max(1)[0] * (1 - dones)
        q_targets = q_targets.unsqueeze(1)

        # 计算当前Q值
        q_values = self.model(states).gather(1, actions)

        # 更新模型
        loss = loss_fn(q_values, q_targets)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        # 更新探索率
        self.epsilon = max(self.epsilon * self.epsilon_decay, self.epsilon_min)

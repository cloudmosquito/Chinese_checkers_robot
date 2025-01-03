# 中国跳棋机器人

本项目目的是实现一个中国跳棋机器人，包括中国跳棋模拟器，棋盘的视觉识别，以及跳棋决策AI。

## 文件结构

```bash
├─figs                      # 图片文件
│  ├─processed              # 处理后的图片
│  └─raw                    # 原始图片
├─vision                    # 视觉相关代码
|  ├─main.py
|  ├─detection.py           # 预处理 + 检测圆形
|  ├─classification.py      # 圆形分类
|  ├─visualization.py       # 可视化
|  └─read_BGR_HSV.py        # 鼠标点击读取像素BGR和HSV信息
├─game
│  └─chinese_chess_play.py  # 跳棋游戏
├─rl_decision               # 跳棋决策AI，用强化学习训练
|  ├─rl_agent_dqn.py
|  ├─rl_env.py
|  ├─rl_reward_model.py
|  └─rl_train.py
├─RREADME.md                # 说明文档
└─requirements.txt          # 依赖项
```

## 依赖项

本项目要使用到的库有：

- matplotlib==3.8.2
- numpy==1.24.4
- opencv_python==4.10.0.84
- scikit_learn==1.3.2
- torch==2.5.1

可通过以下命令安装

```bash
pip install -r requirements.txt
```
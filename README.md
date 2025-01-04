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
|  ├─main.py
|  ├─comm.py                  # 与机械臂通信
|  ├─drawer.py                # 绘制棋盘
|  ├─menu.py                  # 主菜单UI
|  ├─mcts_agent.py            # 基于MCTS算法的AI
│  └─chinese_checkers_play.py  # 跳棋游戏
|
├─RREADME.md                # 说明文档
└─requirements.txt          # 依赖项
```

## 依赖项

本项目要使用到的库有：

- matplotlib==3.8.2
- numpy==1.24.4
- opencv_python==4.10.0.84
- pyttsx3==2.98
- scikit_learn==1.3.2

可通过以下命令安装

```bash
pip install -r requirements.txt
```
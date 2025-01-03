from chinese_chess_play import ChineseCheckersApp
from mcts_agent import MCTSAgent
import tkinter as tk
import threading
import socket
import time

class comm:
  def __init__(self, ai, app):
      # 初始参数
      self.initial_height = 90      # 初始高度
      self.grab_height = 75         # 抓取下降高度
      self.release_height = 80      # 释放下降高度
      self.speed = 2000             # 移动速度
      self.ai = ai
      self.app = app
      
  def generate_set_coords_command(self, coords, speed = 500):
      """
      根据坐标生成Socket格式的set_coords命令。
      :param coords: 坐标列表 [x, y, z, rx, ry, rz]
      :param speed: 移动速度
      :return: 格式化的命令字符串
      """
      return f"set_coords({','.join(map(str, coords))},{speed})"

  def send_command_to_robot(self, socket, command):
      """
      通过Socket发送命令到机器人。
      :param socket: 已连接的Socket对象
      :param command: 要发送的命令字符串
      """
      try:
          socket.send(bytes(command, encoding='utf-8'))
          print(f"发送命令: {command}")
      except socket.error as e:
          print("发送数据时出现错误:", e)

      try:
          data = str(socket.recv(1024))
          print("机械臂返回信息:", data[2:-1])
      except socket.error as e:
          print("接收数据时出现错误:", e)

  def act(self):
    if self.ai.need_send_comm_to_robot:
      start_x, start_y = self.ai.start_pos[0], self.ai.start_pos[1]
      target_x, target_y = self.ai.target_pos[0], self.ai.target_pos[1]
      # 生成操作步骤
      steps = [
          # 1. 下降抓取
          [start_x, start_y, self.grab_height, -179, 0, 0],
          # 2. 升高
          [start_x, start_y, self.initial_height, -179, 0, 0],
          # 3. 移动至目标点
          [target_x, target_y, self.initial_height, -179, 0, 0],
          # 4. 下降释放
          [target_x, target_y, self.release_height, -179, 0, 0],
          # 5. 升高到初始高度
          [target_x, target_y, self.initial_height, -179, 0, 0],
      ]

      # 遍历操作步骤并发送命令
      for step_coords in steps:
          command = self.generate_set_coords_command(step_coords, speed=self.speed)
          self.send_command_to_robot(sk, command)
          time.sleep(5)  # 等待机械臂完成动作
      self.app.ai_ok = True
      self.app.need_draw_path = True
      self.ai.pos_found = False
    threading.Timer(0.001, self.act).start()

    
if __name__ == '__main__':
    # 初始化Socket连接
    sk = socket.socket()
    host = '192.168.137.186'  # 修改为机械臂IP
    port = 5001  # 修改为机械臂端口
    try:
        sk.connect((host, port))
        print("TCP客户端启动成功")
    except socket.error as e:
        print("连接失败:", e)
        exit()
    root = tk.Tk()
    app = ChineseCheckersApp(root, ChineseCheckersApp.PlayerNum.FOR2PLAYER, ChineseCheckersApp.GameMode.PVE, [4])
    ai_player1 = MCTSAgent(app, 4)
    robot_comm = comm(ai_player1, app)
    # ai_player2 = MCTSAgent(app, 5)
    app.play()
    threading.Thread(target=robot_comm.act, daemon=True).start()
    threading.Thread(target=ai_player1.run, daemon=True).start()
    # threading.Thread(target=ai_player2.run, daemon=True).start()
    root.mainloop()

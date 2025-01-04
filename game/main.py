from menu import MainMenu
import tkinter as tk
import socket

is_playing_simulation = True
    
if __name__ == '__main__':
    # 初始化Socket连接
    sk = socket.socket()
    if not is_playing_simulation:
        host = '192.168.137.186'  # 修改为机械臂IP
        port = 5001  # 修改为机械臂端口
        try:
            sk.connect((host, port))
            print("TCP客户端启动成功")
        except socket.error as e:
            print("连接失败:", e)
            exit()
    root = tk.Tk()
    MainMenu(root, sk, is_playing_simulation)
    root.mainloop()

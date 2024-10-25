import cv2
import numpy as np

# 回调函数，用于在点击鼠标时获取 BGR 值和 HSV 值
def get_hsv_value(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:  # 左键点击事件
        # 从 BGR 图像中获取像素值
        b, g, r = image[y, x]
        
        # 将 BGR 转换为 RGB
        rgb_pixel = np.array([r, g, b], dtype=np.uint8)
        
        # 将 RGB 转换为 HSV
        hsv_pixel = cv2.cvtColor(rgb_pixel.reshape(1, 1, 3), cv2.COLOR_RGB2HSV)[0][0]
        
        print(f"Pixel at ({x}, {y}) - BGR: ({b}, {g}, {r}), HSV: {hsv_pixel}")

# 读取图像
image_path = 'figs/raw/fig2.jpg'  # 修改为你的图像路径
image = cv2.imread(image_path)

# 创建窗口并设置鼠标回调
cv2.namedWindow('Image', cv2.WINDOW_NORMAL)
cv2.resizeWindow('Image', 800, 600)
cv2.setMouseCallback('Image', get_hsv_value)

while True:
    cv2.imshow('Image', image)
    if cv2.waitKey(1) & 0xFF == 27:  # 按 'Esc' 键退出
        break

cv2.destroyAllWindows()

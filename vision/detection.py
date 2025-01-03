import cv2
import numpy as np

def detect_circles(image):
    # 具体参数由相机位置决定
    row = [260, 990]
    column = [720, 1450]
    cropped_image = image[row[0]:row[1], column[0]:column[1]]

    # 转为灰度图像处理
    gray_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)

    # 霍夫圆检测
    circles = cv2.HoughCircles(gray_image, cv2.HOUGH_GRADIENT, dp=1.2, minDist=20, 
                               param1=100, param2=25, minRadius=6, maxRadius=24)

    # 如果检测到圆，返回圆的坐标和半径
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        circles[:,0] += column[0]
        circles[:,1] += row[0]
        return circles
    return []

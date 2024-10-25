import cv2
import numpy as np
from matplotlib import pyplot as plt
from sklearn.cluster import KMeans
import detection
from classification import CircleClassifier
import visualization

image_name = 'fig2.jpg' # TODO 修改成你要处理的图片名称
image_path = f'figs/raw/{image_name}'
image = cv2.imread(image_path)

# 检测圆
circles = detection.detect_circles(image)

# 根据K-means分类
n_colors = 7 # TODO 根据需要调整聚类数
circle_classifier = CircleClassifier(n_colors)
classified_circles = circle_classifier.classify(circles, image)
# print(classified_circles) 

image = visualization.draw_circles(image, classified_circles)

cv2.imwrite(f"figs/processed/result_of_{image_name}", image)

# 转换为RGB显示
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
# 显示结果
plt.figure(figsize=(7, 7))
plt.imshow(image_rgb)
plt.axis('off')
plt.show()

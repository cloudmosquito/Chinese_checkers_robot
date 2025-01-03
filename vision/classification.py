import cv2
import numpy as np
from matplotlib import pyplot as plt
from sklearn.cluster import KMeans
import detection

class CircleClassifier:
    def __init__(self, n_colors=7):
        # 已知颜色与标签的对应关系
        self.known_colors = {
            '黄色': (40, 254, 255),
            '红色': (119, 150, 241),
            '绿色': (126, 237, 163),
            '白色': (231, 255, 255),
            '深蓝色': (185, 152, 133),
            '浅蓝色': (219, 208, 148),
            '棋盘色': (126, 189, 249)
        }
        self.n_colors = n_colors
    
    '''
     @brief      找到最近邻颜色
     @param       bgr: BGR向量
     @retval      颜色字符串
     @note       在聚类完成之后调用
    '''    
    def find_closest_color(self, bgr):
        closest_color = None
        min_distance = float('inf')
        for color_name, known_bgr in self.known_colors.items():
            # 计算颜色之间的欧几里得距离
            distance = np.linalg.norm(bgr - known_bgr)
            if distance < min_distance:
                min_distance = distance
                closest_color = color_name
        return closest_color
    
    '''
     @brief       对图像上的圆进行k-means聚类
     @param       circles: 已经找到的圆列表[[x1,y1,r1], [x2,y2,r2], ...]
     @param       image: 待处理的图像
     @retval      分类结果字典
     @note        在霍夫圆检测后调用
    '''    
    def classify(self, circles, image):
        # 获取圆的颜色信息
        color_data = []
        for (x, y, r) in circles:
            # 创建圆形掩模
            mask = np.zeros(image.shape[:2], dtype=np.uint8)
            cv2.circle(mask, (x, y), 8, 255, -1)
            masked_image = cv2.bitwise_and(image, image, mask=mask)   # 提取圆内像素
            pixels_in_circle = masked_image[mask == 255]   # 只选取掩模内的像素点

            mean_bgr = pixels_in_circle.mean(axis=0).astype(int)
            color_data.append(mean_bgr)  # 保留平均BGR值

        # K-means聚类
        kmeans = KMeans(n_clusters=self.n_colors)
        kmeans.fit(color_data)
        labels = kmeans.labels_
        bgrs = kmeans.cluster_centers_.astype(int)

        # 分类结果字典，保存圆、对应的BGR值和颜色标签
        classified_circles = {i: {'circles': [], 'bgr': bgrs[i], 'label': None} for i in range(self.n_colors)}

        # 寻找最接近的已知颜色并打标签
        for label, (x, y, r) in zip(labels, circles):
            classified_circles[label]['circles'].append((x, y, r))
            classified_circles[label]['label'] = self.find_closest_color(bgrs[label])

        return classified_circles

    




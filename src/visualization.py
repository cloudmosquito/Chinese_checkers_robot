import cv2

'''
 @brief      
 @param       image: 待处理图像
 @param       classified_circles: 圆分类结果字典
   @arg       None
 @retval      image: 画上圆的图像
 @note        None
'''
def draw_circles(image, classified_circles):
    colors = {
        '黄色': (0, 255, 255),
        '红色': (0, 0, 255),
        '绿色': (0, 255, 0),
        '白色': (255, 255, 255),
        '深蓝色': (255, 100, 100),
        '浅蓝色': (255, 0, 0),
        '棋盘色': (100, 200, 255)
    }

    # 可视化结果
    for _, circle_info in classified_circles.items():
        circles_list = circle_info['circles']  # 获取当前标签的圆列表
        label = circle_info['label']
        color = colors.get(label)  # 获取对应的颜色
        
        if color:  # 如果找到了颜色
            for (x, y, r) in circles_list:
                cv2.circle(image, (x, y), r, color, 2)  # 用聚类颜色画圆
                cv2.circle(image, (x, y), 2, (0, 0, 0), 1)  # 黑色中心

    return image  # 返回绘制后的图像

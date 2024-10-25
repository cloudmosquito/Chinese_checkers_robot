
## 文件结构

```
├─figs                  # 图片文件
│  ├─processed          # 处理后的图片
│  └─raw                # 原始图片
├─src                   # 源代码
|  └─main.py
|  └─detection.py       # 预处理 + 检测圆形
|  └─classification.py  # 圆形分类
|  └─visualization.py   # 可视化
├─tools
│  └─read_BGR_HSV.py    # 鼠标点击读取像素BGR和HSV信息
├─RREADME.md            # 说明文档
└─requirements.txt      # 依赖项
```


## 依赖项

本项目要使用到的库有：

- numpy==1.26.3
- opencv-python==4.10.0.84
- scikit-learn==1.3.2
- matplotlib==3.8.2

可通过以下命令安装

```bash
pip install -r requirements.txt
```
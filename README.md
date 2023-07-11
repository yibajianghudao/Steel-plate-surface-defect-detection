# Steel-plate-surface-defect-detection

All code is written in Python and utilizes TensorFlow for model training. The visual interface is created using PyQt6. The application supports three methods of detecting surface defects on steel plates: camera input, video input, and image input. The detected data can be saved either in a database or locally.

File Descriptions:

1. read_data.py:
   Reads the image and label data from the NEU surface defect database (NEU surface defect database, provided by Northeastern University. Link: http://faculty.neu.edu.cn/songkechen/zh_CN/zdylm/263270/list/). This data will be used by the following file, train_model.py.

2. train_model.py:
   Trains the model using the data processed by read_data.py. The trained model is saved as train_model.h5 after 100 epochs. It returns the labels corresponding to the detected defects and their positions for convenient annotation box drawing.

3. defunction.py:
   A collection of functions used in the code.

4. detection_camera_local.py:
   Detects defects using a camera and saves the data locally.

5. detection_camera_database.py:
   Detects defects using a camera and saves the data to a database.

6. detection_video_local.py:
   Detects defects using a video and saves the data locally.

7. detection_video_database.py:
   Detects defects using a video and saves the data to a database.

8. detection_image.py:
   Detects defects using an image. It supports either a collection of images (an entire folder) or a single image.

9. main.py:
   Creates a visual interface using PyQt6 and runs the code.

10. make_video.py:
    Creates a video for use with virtual cameras.

11. write_chart.py:
    Generates a bar chart showing the quantity of each defect type.


# 钢板表面缺陷检测

  所有代码使用python编写，使用tensorflow训练模型，使用pyqt6制作可视化界面，可以使用摄像头，视频，图片三种方式检测钢板表面缺陷
  ，可以对检测数据使用数据库和本地两种保存方式

代码文件介绍：

1.read_data.py
  使用NEU-DET目录下的数据集（NEU surface defect database，来自东北大学。链接：http://faculty.neu.edu.cn/songkechen/zh_CN/zdylm/263270/list/）
将图片数据和标签数据读取出来以便下面的train_model.py调用。

2.train_model.py
  使用read_data.py处理过的数据进行模型的训练，train_model.h5为100轮训练出的模型，将会对识别的图像返回缺陷对应的标签和缺陷的位置(方便绘制标注框)

3.defuction.py
  代码中使用到的函数汇总

4.detection_camera_local.py
  使用摄像头进行缺陷的检测并将数据保存到本地
  detection_camera_database.py
  使用摄像头进行缺陷的检测并将数据保存到数据库

5.detection_video_local.py
  使用视频进行缺陷的检测并将数据保存到本地
  detection_video_database.py
  使用视频进行缺陷的检测并将数据保存到数据库

6.detection_image.py
  使用图片进行缺陷的检测，可以使用图片集(一整个文件夹)或单个图片

7.main.py
  使用pyqt6制作可视化界面并进行代码的运行

8.make_video.py
  制作虚拟摄像头使用的视频

9.write_chart.py
  绘制缺陷种类-数量柱形图

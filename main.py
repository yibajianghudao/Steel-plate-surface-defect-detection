import sys
import time
from io import StringIO

import cv2
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QDialog
from PyQt6.QtWidgets import QComboBox, QFileDialog, QPushButton

from detection_camera_database import MainWindowDC as MainWindowDB
from detection_camera_local import MainWindowDC as MainWindowLC
from detection_image import image_detection
from detection_imageset import image_detection as imageset_detection
from detection_video_local import MainWindowDC as MainWindowLV
from train_model import train_main


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("钢板缺陷检测可视化界面")
        self.setGeometry(100, 100, 800, 600)

        self.label = QLabel("主要功能", self)
        self.label.setGeometry(375, 150, 200, 30)

        self.train_button = QPushButton("训练模型", self)
        self.train_button.setGeometry(300, 200, 200, 50)
        self.train_button.clicked.connect(self.open_train_model_window)

        self.detect_button = QPushButton("模型检测", self)
        self.detect_button.setGeometry(300, 270, 200, 50)
        self.detect_button.clicked.connect(self.model_detection)



    def open_train_model_window(self):
        self.label.setText("正在进行训练模型...")
        train_window = TrainModelWindow(self)
        train_window.exec()

    def model_detection(self):
        self.label.setText("正在进行模型检测...")
        detection = ModelDetectionWindow(self)
        detection.exec()



class TrainModelWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Train Model")
        self.setGeometry(100, 100, 400, 400)

        self.label_path_label = QLabel("标签的路径：", self)
        self.label_path_label.setGeometry(50, 50, 100, 30)
        self.label_path_input = QLineEdit(self)
        self.label_path_input.setGeometry(160, 50, 200, 30)
        self.label_path_input.setText(r'.\NEU-DET\ANNOTATIONS_test\\')  # 设置默认值

        self.image_path_label = QLabel("图片的路径：", self)
        self.image_path_label.setGeometry(50, 100, 100, 30)
        self.image_path_input = QLineEdit(self)
        self.image_path_input.setGeometry(160, 100, 200, 30)
        self.image_path_input.setText(r'.\NEU-DET\IMAGES_test\\')  # 设置默认值

        self.model_name_label = QLabel("模型保存的地址和文件名：", self)
        self.model_name_label.setGeometry(50, 150, 150, 30)
        self.model_name_input = QLineEdit(self)
        self.model_name_input.setGeometry(200, 150, 160, 30)
        self.model_name_input.setText("train_model.h5")  # 设置默认值

        self.rounds_num_label = QLabel("模型训练的轮次：", self)
        self.rounds_num_label.setGeometry(50, 200, 200, 30)
        self.rounds_num_input = QLineEdit(self)
        self.rounds_num_input.setGeometry(200, 200, 160, 30)
        self.rounds_num_input.setText("1")  # 设置默认值

        self.train_button = QPushButton("开始训练", self)
        self.train_button.setGeometry(150, 250, 100, 30)
        self.train_button.clicked.connect(self.start_training)

    def start_training(self):
        self.close()  # 关闭训练窗口

        label_path = self.label_path_input.text()
        image_path = self.image_path_input.text()
        model_name = self.model_name_input.text()
        rounds_num = self.rounds_num_input.text()

        rounds_num = int(rounds_num)

        # 重定向标准输出
        old_stdout = sys.stdout
        redirected_output = StringIO()
        sys.stdout = redirected_output

        time.sleep(3)

        # 调用训练模型函数
        train_main(label_path, image_path, model_name, rounds_num)

        # 恢复标准输出
        sys.stdout = old_stdout

        self.parent().label.setText("训练模型完毕")

        # 创建一个新的窗口来显示输出文本
        output_window = QDialog(self.parent())
        output_window.setWindowTitle("训练完成")
        output_window.setGeometry(100, 100, 400, 400)

        # 显示训练信息的标签
        model_name_label = QLabel(f"模型名：{model_name}", output_window)
        model_name_label.setGeometry(10, 140, 300, 30)

        rounds_num_label = QLabel(f"训练轮次：{rounds_num}", output_window)
        rounds_num_label.setGeometry(10, 170, 300, 30)

        output_window.exec()


class ModelDetectionWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Model Detection")
        self.setGeometry(100, 100, 800, 600)

        self.label = QLabel("模型检测功能", self)
        self.label.setGeometry(375, 150, 200, 30)

        self.train_button = QPushButton("摄像头检测", self)
        self.train_button.setGeometry(300, 200, 200, 50)
        self.train_button.clicked.connect(self.detect_camera_button)

        self.image_button = QPushButton("图片检测", self)
        self.image_button.setGeometry(300, 270, 200, 50)
        self.image_button.clicked.connect(self.detect_image_button)

        self.save_button = QPushButton("视频检测", self)
        self.save_button.setGeometry(300, 340, 200, 50)
        self.save_button.clicked.connect(self.detect_video_button)

    def detect_camera_button(self):
        self.label.setText("正在进行摄像头检测...")
        select_window = CameraSaveSelectWindow(self)
        select_window.exec()

    def detect_image_button(self):
        self.label.setText("正在进行图片检测...")
        image_window = ImageSaveSelectWindow(self)
        image_window.exec()

    def detect_video_button(self):
        self.label.setText("正在进行视频检测...")
        video_window = LocalVideoDetectionWindow(self)
        video_window.exec()


class CameraSaveSelectWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Select Save Mode")
        self.setGeometry(100, 100, 800, 600)

        self.label = QLabel("选择数据保存方式", self)
        self.label.setGeometry(375, 150, 200, 30)

        self.local_button = QPushButton("保存到本地", self)
        self.local_button.setGeometry(300, 200, 200, 50)
        self.local_button.clicked.connect(self.detect_local_button)

        self.database_button = QPushButton("保存到数据库", self)
        self.database_button.setGeometry(300, 300, 200, 50)
        self.database_button.clicked.connect(self.detect_database_button)

    def detect_local_button(self):
        self.label.setText("保存到本地")
        camera_window = LocalCameraDetectionWindow(self)
        camera_window.exec()

    def detect_database_button(self):
        self.label.setText("保存到数据库")
        camera_window = DataBaseCameraDetectionWindow(self)
        camera_window.exec()


class LocalCameraDetectionWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Local Save Camera Detection")
        self.setGeometry(100, 100, 800, 600)

        self.camera_label = QLabel("选择摄像头：", self)
        self.camera_label.setGeometry(50, 100, 150, 30)

        self.camera_combobox = QComboBox(self)
        self.camera_combobox.setGeometry(210, 100, 150, 30)

        # 填充摄像头下拉选项
        self.populate_camera_combobox()

        self.model_file_label = QLabel("模型文件：", self)
        self.model_file_label.setGeometry(50, 150, 150, 30)

        self.model_file_input = QLineEdit(self)
        self.model_file_input.setGeometry(210, 150, 250, 30)
        self.model_file_input.setText(r".\model.h5")  # 设置默认值

        self.select_file_button = QPushButton("选择模型", self)
        self.select_file_button.setGeometry(460, 150, 100, 30)
        self.select_file_button.clicked.connect(self.select_model)

        self.local_file_label = QLabel("保存的文件夹路径(需已创建)：", self)
        self.local_file_label.setGeometry(50, 200, 160, 30)
        self.local_file_input = QLineEdit(self)
        self.local_file_input.setGeometry(210, 200, 250, 30)
        self.local_file_input.setText(r".\save_camera\\")  # 设置默认值

        self.save_file_name = self.local_file_input.text()

        self.start_button = QPushButton("开始检测", self)
        self.start_button.setGeometry(300, 300, 150, 50)
        self.start_button.clicked.connect(self.start_detection)

        self.model_file = ""
        self.VideoCapture_num = 0  # 默认选择第一个摄像头

    def select_model(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "选择模型文件", "", "模型文件 (*.h5)")
        if file_name:
            self.model_file = file_name
            self.model_file_input.setText(file_name)

    def start_detection(self):
        self.model_file = self.model_file_input.text()
        model_file = self.model_file
        save_file_name = self.save_file_name
        videoCapture_num = self.VideoCapture_num
        window = MainWindowLC(model_file, save_file_name, videoCapture_num, self)
        window.showMaximized()
        window.start_detection_()

    def populate_camera_combobox(self):
        camera_devices = self.get_camera_devices()  # 获取设备上所有的摄像头
        for i, camera_device in enumerate(camera_devices):
            self.camera_combobox.addItem(f"摄像头 {i + 1}")

        # 监听下拉框的选择事件
        self.camera_combobox.currentIndexChanged.connect(self.update_selected_camera_index)

    def update_selected_camera_index(self, index):
        self.VideoCapture_num = index

    def get_camera_devices(self):
        camera_devices = []
        index = 0
        while True:
            cap = cv2.VideoCapture(index)
            if not cap.read()[0]:
                break
            camera_devices.append(index)
            cap.release()
            index += 1
        return camera_devices


class DataBaseCameraDetectionWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Local Save Camera Detection")
        self.setGeometry(100, 100, 800, 600)

        self.camera_label = QLabel("选择摄像头：", self)
        self.camera_label.setGeometry(50, 50, 150, 30)

        self.camera_combobox = QComboBox(self)
        self.camera_combobox.setGeometry(200, 50, 150, 30)

        # 填充摄像头下拉选项
        self.populate_camera_combobox()

        self.model_file_label = QLabel("模型文件：", self)
        self.model_file_label.setGeometry(50, 150, 100, 30)

        self.model_file_input = QLineEdit(self)
        self.model_file_input.setGeometry(200, 150, 300, 30)
        self.model_file_input.setText(r".\model.h5")  # 设置默认值

        self.select_file_button = QPushButton("选择模型", self)
        self.select_file_button.setGeometry(500, 150, 100, 30)
        self.select_file_button.clicked.connect(self.select_model)

        self.Database_address_label = QLabel("数据库地址：", self)
        self.Database_address_label.setGeometry(50, 200, 100, 30)
        self.Database_address_input = QLineEdit(self)
        self.Database_address_input.setGeometry(200, 200, 300, 30)
        self.Database_address_input.setText(r"localhost")

        self.User_name_label = QLabel("用户名：", self)
        self.User_name_label.setGeometry(50, 250, 100, 30)
        self.User_name_input = QLineEdit(self)
        self.User_name_input.setGeometry(200, 250, 300, 30)
        self.User_name_input.setText(r"123")

        self.User_passwd_label = QLabel("登录密码：", self)
        self.User_passwd_label.setGeometry(50, 300, 100, 30)
        self.User_passwd_input = QLineEdit(self)
        self.User_passwd_input.setGeometry(200, 300, 300, 30)
        self.User_passwd_input.setText(r"123")

        self.Database_name_label = QLabel("数据库名：", self)
        self.Database_name_label.setGeometry(50, 350, 100, 30)
        self.Database_name_input = QLineEdit(self)
        self.Database_name_input.setGeometry(200, 350, 300, 30)
        self.Database_name_input.setText(r"defects")

        self.time_interval_label = QLabel("两张表之间间隔的秒数：", self)
        self.time_interval_label.setGeometry(50, 400, 150, 30)
        self.time_interval_input = QLineEdit(self)
        self.time_interval_input.setGeometry(200, 400, 300, 30)
        self.time_interval_input.setText(r"60")

        self.Database_address = self.Database_address_input.text()
        self.User_name = self.User_name_input.text()
        self.User_passwd = self.User_passwd_input.text()
        self.Database_name = self.Database_name_input.text()
        self.time_interval = self.time_interval_input.text()

        self.start_button = QPushButton("开始检测", self)
        self.start_button.setGeometry(220, 450, 150, 30)
        self.start_button.clicked.connect(self.start_detection)

        self.model_file = ""
        self.VideoCapture_num = 0  # 默认选择第一个摄像头

    def select_model(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "选择模型文件", "", "模型文件 (*.h5)")
        if file_name:
            self.model_file = file_name
            self.model_file_input.setText(file_name)

    def start_detection(self):
        self.model_file = self.model_file_input.text()
        model_file = self.model_file
        time_interval = self.time_interval
        time_num = int(time_interval) * 1000
        host = self.Database_address_input.text()
        user = self.User_name_input.text()
        password = self.User_passwd_input.text()
        database = self.Database_name_input.text()
        videoCapture_num = self.VideoCapture_num
        window = MainWindowDB(model_file, time_num, host, user, password, database, videoCapture_num,
                              parent_window=self)
        window.showMaximized()
        window.start_detection_(enable_database=True)

    def populate_camera_combobox(self):
        camera_devices = self.get_camera_devices()  # 获取设备上所有的摄像头
        for i, camera_device in enumerate(camera_devices):
            self.camera_combobox.addItem(f"摄像头 {i + 1}")

        # 监听下拉框的选择事件
        self.camera_combobox.currentIndexChanged.connect(self.update_selected_camera_index)

    def update_selected_camera_index(self, index):
        self.VideoCapture_num = index

    def get_camera_devices(self):
        camera_devices = []
        index = 0
        while True:
            cap = cv2.VideoCapture(index)
            if not cap.read()[0]:
                break
            camera_devices.append(index)
            cap.release()
            index += 1
        return camera_devices


class ImageSaveSelectWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Image Select")
        self.setGeometry(100, 100, 800, 600)

        self.label = QLabel("选择图片输入方式", self)
        self.label.setGeometry(375, 150, 200, 30)

        self.train_button = QPushButton("图片集", self)
        self.train_button.setGeometry(300, 200, 200, 50)
        self.train_button.clicked.connect(self.open_ImageSetDetection_window)

        self.detect_button = QPushButton("单个图片", self)
        self.detect_button.setGeometry(300, 270, 200, 50)
        self.detect_button.clicked.connect(self.open_ImageDetection_window)

    def open_ImageSetDetection_window(self):
        self.label.setText("正在进行图片集检测...")
        select_window = ImageSetDetection_window(self)
        select_window.exec()

    def open_ImageDetection_window(self):
        self.label.setText("正在进行单个图片检测...")
        image_window = ImageDetectionWindow(self)
        image_window.exec()


class ImageSetDetection_window(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Image Set Detection")
        self.setGeometry(100, 100, 800, 600)

        self.label = QLabel("图片集检测功能", self)
        self.label.setGeometry(200, 50, 200, 30)

        self.imageset_file_label = QLabel("图片所在文件夹：", self)
        self.imageset_file_label.setGeometry(50, 100, 100, 30)

        self.imageset_file_input = QLineEdit(self)
        self.imageset_file_input.setGeometry(160, 100, 300, 30)
        self.imageset_file_input.setText(r".\image")  # 设置默认值

        self.imageset_file_button = QPushButton("选择图片所在文件夹", self)
        self.imageset_file_button.setGeometry(460, 100, 150, 30)
        self.imageset_file_button.clicked.connect(self.select_imageset)

        self.image_output_label = QLabel("图片输出文件夹：", self)
        self.image_output_label.setGeometry(50, 150, 100, 30)

        self.image_output_input = QLineEdit(self)
        self.image_output_input.setGeometry(160, 150, 300, 30)
        self.image_output_input.setText(r'.\image_detection')  # 设置默认值

        self.image_output_button = QPushButton("选择输出图片文件夹", self)
        self.image_output_button.setGeometry(460, 150, 150, 30)
        self.image_output_button.clicked.connect(self.select_output_imageset)

        self.model_file_label = QLabel("模型文件：", self)
        self.model_file_label.setGeometry(50, 200, 100, 30)

        self.model_file_input = QLineEdit(self)
        self.model_file_input.setGeometry(160, 200, 300, 30)
        self.model_file_input.setText(r".\model.h5")  # 设置默认值

        self.select_file_button = QPushButton("选择模型", self)
        self.select_file_button.setGeometry(460, 200, 150, 30)
        self.select_file_button.clicked.connect(self.select_model)

        self.start_button = QPushButton("开始检测", self)
        self.start_button.setGeometry(220, 300, 150, 30)
        self.start_button.clicked.connect(self.start_detection)

        self.model_file = './model.h5'

    def select_model(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "选择模型文件", "", "模型文件 (*.h5)")
        if file_name:
            self.model_file = file_name
            self.model_file_input.setText(file_name)

    def select_imageset(self):
        file_name = QFileDialog.getExistingDirectory(self, "选择图片所在文件夹")
        if file_name:
            self.imageset_file_input.setText(file_name)

    def select_output_imageset(self):
        file_name = QFileDialog.getExistingDirectory(self, "选择图片输出文件夹")
        if file_name:
            self.image_output_input.setText(file_name)

    def start_detection(self):
        image_folder = self.imageset_file_input.text()
        output_folder = self.image_output_input.text()
        model_file = self.model_file
        imageset_detection(image_folder, output_folder, model_file)
        self.label.setText("图片检测已完毕！")


class ImageDetectionWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Image Detection")
        self.setGeometry(100, 100, 800, 600)

        self.image_file_label = QLabel("图片文件：", self)
        self.image_file_label.setGeometry(50, 150, 100, 30)

        self.image_file_input = QLineEdit(self)
        self.image_file_input.setGeometry(160, 150, 300, 30)
        self.image_file_input.setText(r".\image.jpg")  # 设置默认值

        self.select_image_file_button = QPushButton("选择图片", self)
        self.select_image_file_button.setGeometry(380, 150, 100, 30)
        self.select_image_file_button.clicked.connect(self.select_image)

        self.model_file_label = QLabel("模型文件：", self)
        self.model_file_label.setGeometry(50, 200, 100, 30)

        self.model_file_input = QLineEdit(self)
        self.model_file_input.setGeometry(160, 200, 300, 30)
        self.model_file_input.setText(r".\model.h5")  # 设置默认值

        self.select_file_button = QPushButton("选择模型", self)
        self.select_file_button.setGeometry(380, 200, 100, 30)
        self.select_file_button.clicked.connect(self.select_model)

        self.start_button = QPushButton("开始检测", self)
        self.start_button.setGeometry(220, 300, 150, 30)
        self.start_button.clicked.connect(self.start_detection)

        self.image_file = ""
        self.model_file = ""

    def select_model(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "选择模型文件", "", "模型文件 (*.h5)")
        if file_name:
            self.model_file = file_name
            self.model_file_input.setText(file_name)

    def select_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "选择图片文件", "", "图片文件 (*.jpg)")
        if file_name:
            self.image_file = file_name
            self.image_file_input.setText(file_name)

    def start_detection(self):
        model_file = self.model_file
        image_file = self.image_file
        if not model_file:
            model_file = r".\model.h5"
        if not image_file:
            image_file = r".\image.jpg"
        image_detection(image_file, model_file)


class LocalVideoDetectionWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Local Save Camera Detection")
        self.setGeometry(100, 100, 800, 600)

        self.model_file_label = QLabel("模型文件：", self)
        self.model_file_label.setGeometry(50, 150, 150, 30)

        self.model_file_input = QLineEdit(self)
        self.model_file_input.setGeometry(210, 150, 250, 30)
        self.model_file_input.setText(r".\model.h5")  # 设置默认值

        self.select_file_button = QPushButton("选择模型", self)
        self.select_file_button.setGeometry(460, 150, 100, 30)
        self.select_file_button.clicked.connect(self.select_model)

        self.video_file_label = QLabel("视频文件：", self)
        self.video_file_label.setGeometry(50, 200, 150, 30)

        self.video_file_input = QLineEdit(self)
        self.video_file_input.setGeometry(210, 200, 250, 30)
        self.video_file_input.setText(r".\video.mp4")  # 设置默认值

        self.select_video_file_button = QPushButton("选择视频", self)
        self.select_video_file_button.setGeometry(460, 200, 100, 30)
        self.select_video_file_button.clicked.connect(self.select_video)

        self.local_file_label = QLabel("保存的文件夹路径(需已创建)：", self)
        self.local_file_label.setGeometry(50, 250, 160, 30)
        self.local_file_input = QLineEdit(self)
        self.local_file_input.setGeometry(210, 250, 250, 30)
        self.local_file_input.setText(r".\save_video\\")  # 设置默认值

        self.save_file_name = self.local_file_input.text()

        self.start_button = QPushButton("开始检测", self)
        self.start_button.setGeometry(300, 300, 150, 50)
        self.start_button.clicked.connect(self.start_detection)

        self.model_file = ""
        self.video_file = ""

    def select_model(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "选择模型文件", "", "模型文件 (*.h5)")
        if file_name:
            self.model_file = file_name
            self.model_file_input.setText(file_name)

    def select_video(self):
        video_file_name, _ = QFileDialog.getOpenFileName(self, "选择视频文件", "", "视频文件 (*.mp4)")
        if video_file_name:
            self.video_file = video_file_name
            self.video_file_input.setText(video_file_name)

    def start_detection(self):
        model_file = self.model_file
        save_file_name = self.save_file_name
        video_file = self.video_file
        print(model_file)
        print(save_file_name)
        print(video_file)
        if not model_file:
            model_file = r'.\model.h5'
        if not video_file:
            video_file = r'.\video.mp4'

        window = MainWindowLV(model_file, video_file, save_file_name, self)
        window.showMaximized()
        window.start_detection_()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())

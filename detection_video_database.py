import sys
import cv2
import threading
import time
import os
import numpy as np
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget

from defuction import model_detection
from defuction import data_store, data_select
from datetime import datetime


class MainWindowDC(QMainWindow):
    def __init__(self, model_file, video_file,time_num,host, user, password, database, parent_window=None):
        super().__init__(parent_window)
        self.host = host
        self.user = user
        self.password = password
        self.database = database

        self.bbox = [2, 2, 100, 100]
        self.label = ''
        self.cap = cv2.VideoCapture(video_file)
        self.yn = True

        self.data_defects = {'crazing': 0, 'inclusion': 0, 'patches': 0, 'pitted_surface': 0, 'rolled-in_scale': 0,
                             'scratches': 0}
        self.num_defects = 0

        file_name = os.path.basename(video_file)
        self.file_name_without_extension = os.path.splitext(file_name)[0]

        self.name = self.file_name_without_extension+'_labels_number_0'
        self.model_file = model_file

        self.image_label = QLabel(self)
        self.image_label.setScaledContents(True)  # 图像自适应窗口大小

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.image_label)

        self.widget = QWidget()
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.display_image)
        self.timer.start(30)

        self.thread2 = None
        self.thread3 = None

        if time_num != -1:
            self.update_label_timer = QTimer(self)
            self.update_label_timer.timeout.connect(self.update_label_name)
            self.update_label_timer.start(time_num)

    def update_label_name(self):
        current_time = datetime.now()
        formatted_time = current_time.strftime("%m%d%H%M")
        self.name = f'{self.file_name_without_extension}_labels_number_{formatted_time}'


    def display_image(self):
        ret, frame = self.cap.read()
        if ret:
            start_point = (int(self.bbox[0]), int(self.bbox[1]))
            end_point = (int(self.bbox[2]), int(self.bbox[3]))
            # 边框颜色
            color = (255, 0, 0)
            # 边框线条粗细
            thickness = 1
            image_with_bbox = cv2.rectangle(frame, start_point, end_point, color, thickness)
            label_position = (start_point[0], start_point[1] - 10)

            label_size, _ = cv2.getTextSize(self.label, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)

            label_scale = 1.0  # 默认的标签大小因子

            if label_position[1] - label_size[1] <= 0:
                # 如果标签上方空间不足，将标签放在框的内部
                label_position = (start_point[0], start_point[1] + label_size[1] + 10)
                label_scale = 1
            if self.label == "rolled-in_scale" or self.label == "pitted_surface":
                label_scale = 0.6
            cv2.putText(image_with_bbox, self.label, label_position, cv2.FONT_HERSHEY_SIMPLEX, label_scale,
                        (0, 0, 255), 2)

            # 将OpenCV图像转换为QImage
            image_rgb = cv2.cvtColor(image_with_bbox, cv2.COLOR_BGR2RGB)
            h, w, ch = image_rgb.shape
            q_image = QImage(image_rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            self.image_label.setPixmap(pixmap)
        else:
            self.close()

    def model_use(self):
        while self.yn:
            ret, frame = self.cap.read()
            if not ret:
                break
            self.bbox, self.label = model_detection(frame, self.model_file)
            self.data_defects[self.label] += 1
            self.num_defects += 1

    def data_update(self):
        while self.yn:
            data_store(self.data_defects, self.name, self.host, self.user, self.password, self.database)
            time.sleep(1)

    def start_detection_(self, enable_database=False):
        self.thread2 = threading.Thread(target=self.model_use)
        if enable_database:
            self.thread3 = threading.Thread(target=self.data_update)

        self.thread2.start()
        if enable_database:
            self.thread3.start()

    def closeEvent(self, event):
        self.yn = False

        if self.cap:
            self.cap.release()

        self.timer.stop()

        self.thread2.join()
        if self.thread3 is not None:
            self.thread3.join()

        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    model_file = r'.\model.h5'
    video_file = r'.\video.mp4'
    time_num = -1
    host = 'localhost'
    user = '123'
    password = '123'
    database = 'defects_video'
    parent_window = None
    window = MainWindowDC(model_file,video_file,time_num,host,user,password,database,parent_window=parent_window)
    window.showMaximized()
    window.start_detection_(enable_database=True)
    sys.exit(app.exec())
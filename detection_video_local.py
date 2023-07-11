import os
import sys
import cv2
import threading
import time
import numpy as np
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from datetime import datetime

from defuction import model_detection


class MainWindowDC(QMainWindow):
    def __init__(self, model_file, video_file, save_file, parent_window=None):
        super().__init__(parent_window)

        self.bbox = [2, 2, 100, 100]
        self.label = ''
        self.cap = cv2.VideoCapture(video_file)
        self.yn = True
        self.data_defects = {'crazing': 0, 'inclusion': 0, 'patches': 0, 'pitted_surface': 0, 'rolled-in_scale': 0,
                             'scratches': 0}
        self.num_defects = 0
        self.model_file = model_file

        file_name_base = os.path.basename(video_file)
        self.file_name = os.path.splitext(file_name_base)[0]

        self.save_file = save_file
        self.save_file_name = 'label_data.txt'
        self.name = self.save_file_name

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

        self.save_timer = QTimer(self)
        self.save_timer.timeout.connect(self.save_labels_to_file)
        self.save_interval = 10000  # 保存间隔时间（以毫秒为单位）


    def display_image(self):
        ret, frame = self.cap.read()
        try:
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
        except:
            print("Assertion error occurred:")
            pass

    def model_use(self):
        self.save_timer.start(self.save_interval)
        while self.yn:
            ret, frame = self.cap.read()
            if frame is not None and frame.any():
                self.bbox, self.label = model_detection(frame, self.model_file)
                self.data_defects[self.label] += 1
                self.num_defects += 1
                self.save_labels_to_file()

    def save_labels_to_file(self):
        file_path_name = self.save_file + '_' + self.file_name + self.save_file_name
        with open(file_path_name, 'w') as f:
            for label, count in self.data_defects.items():
                f.write(f"{label}: {count}\n")

    def start_detection_(self):
        self.thread2 = threading.Thread(target=self.model_use)
        self.thread2.start()

    def closeEvent(self, event):
        # 停止摄像头检测线程
        self.cap.release()
        self.yn = False

        # 等待线程结束
        self.thread2.join()

        # 保存标签数据到指定文件
        self.save_labels_to_file()

        cv2.destroyAllWindows()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    model_file = r'.\model.h5'
    video_file = r'.\video.mp4'
    save_file_name = r'.\save_video\\'
    parent_window = None
    window = MainWindowDC(model_file, video_file, save_file_name, parent_window)
    window.showMaximized()
    window.start_detection_()
    sys.exit(app.exec())

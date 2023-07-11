import os
import xml.etree.ElementTree as ET
import numpy as np
import cv2
from sklearn.preprocessing import LabelEncoder
from tensorflow.python.keras.utils.np_utils import to_categorical
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

def preprocess_data(xml_folder, image_folder):
    # xml_folder = r'.\\' + xml_folder_latter
    # image_folder = r'.\\' + image_folder_latter

    class_labels = ['crazing', 'inclusion', 'patches', 'pitted_surface', 'rolled-in_scale', 'scratches']

    images = []
    labels = []
    bounding_boxes = []

    for filename in os.listdir(xml_folder):
        if filename.endswith('.xml'):
            tree = ET.parse(os.path.join(xml_folder, filename))
            root = tree.getroot()

            image_filename = root.find('filename').text
            if not image_filename.endswith('.jpg'):
                image_filename += '.jpg'

            objects = root.findall('object')
            for obj in objects:
                object_name = obj.find('name').text
                bndbox = obj.find('bndbox')
                xmin = int(bndbox.find('xmin').text)
                ymin = int(bndbox.find('ymin').text)
                xmax = int(bndbox.find('xmax').text)
                ymax = int(bndbox.find('ymax').text)

                image_path = os.path.join(image_folder, image_filename)
                image = cv2.imread(image_path)

                # 添加原始图像
                images.append(image)
                labels.append(object_name)
                bounding_boxes.append([xmin, ymin, xmax, ymax])

                # 添加翻转图像
                flipped_image = cv2.flip(image, 1)
                images.append(flipped_image)
                labels.append(object_name)
                bounding_boxes.append([xmin, ymin, xmax, ymax])

                # 添加旋转图像
                for angle in [90, 270]:
                    rotated_image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
                    images.append(rotated_image)
                    labels.append(object_name)
                    bounding_boxes.append([xmin, ymin, xmax, ymax])



    images = np.array(images, dtype=object)
    labels = np.array(labels)
    bounding_boxes = np.array(bounding_boxes)

    label_encoder = LabelEncoder()
    encoded_labels = label_encoder.fit_transform(labels)
    one_hot_labels = to_categorical(encoded_labels)

    scaler = MinMaxScaler()
    normalized_images = scaler.fit_transform(images.reshape(-1, 200 * 200 * 3))
    normalized_images = normalized_images.reshape(-1, 200, 200, 3)

    train_images, test_images, train_labels, test_labels, train_bboxes, test_bboxes = train_test_split(
        normalized_images, one_hot_labels, bounding_boxes, test_size=0.2, stratify=one_hot_labels, random_state=42)

    return train_images, test_images, train_labels, test_labels, train_bboxes, test_bboxes


if __name__ == '__main__':
    xml_folder = r'./NEU-DET/ANNOTATIONS/'
    image_folder = r'/NEU-DET/IMAGES/'
    train_images, test_images, train_labels, test_labels, train_bboxes, test_bboxes = preprocess_data(xml_folder, image_folder)

    print("训练集图像数据形状:", train_images.shape)
    print("训练集标签数据形状:", train_labels.shape)
    print("训练集标注框数据形状:", train_bboxes.shape)
    print("测试集图像数据形状:", test_images.shape)
    print("测试集标签数据形状:", test_labels.shape)
    print("测试集标注框数据形状:", test_bboxes.shape)


import os

import cv2

from defuction import model_detection


def image_detection(image_folder, output_folder, model):
    for filename in os.listdir(image_folder):
        if filename.endswith('.jpg') or filename.endswith('.png'):
            image_path = os.path.join(image_folder, filename)
            frame = cv2.imread(image_path)

            bbox, label = model_detection(frame, model)
            start_point = (int(bbox[0]), int(bbox[1]))
            end_point = (int(bbox[2]), int(bbox[3]))
            color = (255, 0, 0)
            thickness = 1
            image_with_bbox = cv2.rectangle(frame, start_point, end_point, color, thickness)

            label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)

            label_position = (start_point[0], start_point[1] - 10)
            label_scale = 1.0

            if label_position[1] - label_size[1] <= 0:
                label_position = (start_point[0], start_point[1] + label_size[1] + 10)
                label_scale = 1
            if label == "rolled-in_scale" or label == "pitted_surface":
                label_scale = 0.6
            cv2.putText(image_with_bbox, label, label_position, cv2.FONT_HERSHEY_SIMPLEX, label_scale, (0, 0, 255), 2)

            output_path = os.path.join(output_folder, filename)
            cv2.imwrite(output_path, image_with_bbox)


if __name__ == "__main__":
    image_folder = r'.\image'
    output_folder = r'.\image_detection'
    model = 'model.h5'
    image_detection(image_folder, output_folder, model)

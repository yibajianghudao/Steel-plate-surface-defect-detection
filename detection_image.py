import cv2
from defuction import model_detection


def image_detection(image, model):
    frame = cv2.imread(image)

    bbox, label = model_detection(frame, model)
    start_point = (int(bbox[0]), int(bbox[1]))
    end_point = (int(bbox[2]), int(bbox[3]))
    # 边框颜色
    color = (255, 0, 0)
    # 边框线条粗细
    thickness = 1
    image_with_bbox = cv2.rectangle(frame, start_point, end_point, color, thickness)
    
    # 获取标签文本的大小
    label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
    
    # 调整标签位置
    label_position = (start_point[0], start_point[1] - 10)
    label_scale = 1.0  # 默认的标签大小因子

    if label_position[1] - label_size[1] <= 0:
        # 如果标签上方空间不足，将标签放在框的内部
        label_position = (start_point[0], start_point[1] + label_size[1] + 10)
        label_scale = 1
    if label == "rolled-in_scale" or label == "pitted_surface":
        label_scale = 0.6
    cv2.putText(image_with_bbox, label, label_position, cv2.FONT_HERSHEY_SIMPLEX,label_scale, (0, 0, 255), 2)
    cv2.imshow('Steel plate surface defect detection', image_with_bbox)

    while cv2.getWindowProperty('Steel plate surface defect detection', cv2.WND_PROP_VISIBLE) >= 1:
        cv2.waitKey(1)

    cv2.destroyAllWindows()


if __name__ == "__main__":
    image_path = 'image.jpg'
    model = 'model.h5'
    image_detection(image_path, model)

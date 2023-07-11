import cv2
import numpy as np
import tensorflow as tf
import pymysql
import cryptography
import matplotlib.pyplot as plt
import os


# 数据采集
def capture_image(source=None):
    if source is None:
        # 未指定数据源时，使用默认摄像头
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()
    else:
        # 指定了图像文件路径时，从文件读取图像
        frame = cv2.imread(source)
        if frame is None:
            raise ValueError("无法读取图像文件")

    return frame


# 数据预处理
def preprocess_image(image):
    # 缩放或剪切到 200x200 大小
    resized_image = cv2.resize(image, (200, 200))

    # 归一化
    normalized_image = resized_image.astype(np.float32) / 255.0
    input_image = np.expand_dims(normalized_image, axis=0)

    return input_image


# 图片检测
def detect_image(image_processed, model_file):
    model = tf.keras.models.load_model(model_file)
    predictions = model.predict(image_processed)
    # 标注框
    xmin = predictions[0][0][0]
    ymin = predictions[0][0][1]
    xmax = predictions[0][0][2]
    ymax = predictions[0][0][3]
    bbox = [xmin, ymin, xmax, ymax]
    # 标签列表
    label_list = predictions[1][0]

    return bbox, label_list


# 提取标签
def label_select(label_list):
    data = label_list
    class_labels = ['crazing', 'inclusion', 'patches', 'pitted_surface', 'rolled-in_scale', 'scratches']
    # class_labels = ['开裂', '内含物', '斑块', '点蚀', '轧制氧化皮', '划痕']
    max_value_index = max(range(len(data)), key=lambda i: data[i])
    max_label = class_labels[max_value_index]

    return max_label


# 绘制缺陷
def label_image(image, bbox):
    start_point = (int(bbox[0]), int(bbox[1]))
    end_point = (int(bbox[2]), int(bbox[3]))
    # 边框颜色
    color = (255, 0, 0)
    # 边框线条粗细
    thickness = 2
    image_with_bbox = cv2.rectangle(image, start_point, end_point, color, thickness)

    # 显示图像
    cv2.imshow('Image with Bounding Box', image_with_bbox)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


# 数据存储
import pymysql

def data_store(data_dict, table_name, host, user, password, database):
    db = pymysql.connect(host=host,
                         user=user,
                         password=password)

    # Check if the database exists
    cursor = db.cursor()
    cursor.execute("SHOW DATABASES")
    databases = cursor.fetchall()

    if (database,) not in databases:
        # Create the database if it doesn't exist
        cursor.execute("CREATE DATABASE {}".format(database))

    # Connect to the specific database
    db = pymysql.connect(host=host,
                         user=user,
                         password=password,
                         database=database)

    cursor = db.cursor()
    create_table_query = '''CREATE TABLE IF NOT EXISTS {} (
                            class VARCHAR(50) PRIMARY KEY,
                            frequency INT
                            )'''.format(table_name)

    cursor.execute(create_table_query)

    for class_name, frequency in data_dict.items():
        insert_query = "INSERT INTO {} (class, frequency) VALUES ('{}', {}) ON DUPLICATE KEY UPDATE frequency = {}".format(
            table_name, class_name, frequency, frequency)
        cursor.execute(insert_query)

    db.commit()

    cursor.close()
    db.close()


# 数据查询
def data_select(table_name):
    # 连接到数据库
    connection = pymysql.connect(host='localhost', user='123', password='123', database='defects')

    # 创建游标对象
    cursor = connection.cursor()

    # 查询数据库中的值
    select_query = "SELECT class, frequency FROM {}".format(table_name)
    cursor.execute(select_query)

    # 将结果存储到字典中
    data = {}
    results = cursor.fetchall()
    for row in results:
        class_name, frequency = row
        data[class_name] = frequency

    return data

    # 关闭游标和数据库连接
    cursor.close()
    connection.close()


# 数据分析
def analyze_data(data):
    # 统计信息
    total_defects = sum(data.values())
    num_defect_types = len(data)
    max_defects = max(data.values())
    min_defects = min(data.values())

    # 缺陷比例
    defect_ratio = {defect_type: count / total_defects * 100 for defect_type, count in data.items()}

    # 打印统计信息和性能指标
    print("统计信息:")
    print(f"总缺陷数: {total_defects}")
    print(f"缺陷类型数: {num_defect_types}")
    print(f"最大缺陷数: {max_defects}")
    print(f"最小缺陷数: {min_defects}")
    print("各缺陷类型比例:")
    for defect_type, ratio in defect_ratio.items():
        print(f"{defect_type}: {ratio:.2f}%")


# 画圆柱图
def visualize_data_from_file(file_path):
    def visualize_data(data):
        # 提取缺陷类型和对应的数量
        defect_types = list(data.keys())
        defect_counts = list(data.values())

        # 设置柱状图的宽度和间隔
        width = 0.5  # 柱状图的宽度
        gap = 0.3  # 相邻圆柱的间隔

        # 计算X轴刻度位置
        x_ticks = range(len(defect_types))

        # 创建柱状图
        plt.bar(x_ticks, defect_counts, width=width, align='center')

        # 设置X轴刻度标签
        plt.xticks(x_ticks, defect_types)

        # 调整刻度位置，增加相邻圆柱的间隔
        plt.xlim(x_ticks[0] - gap, x_ticks[-1] + gap)

        # 设置X轴标签、Y轴标签和图表标题
        plt.xlabel('缺陷类型')
        plt.ylabel('数量')
        plt.title('缺陷类型统计')

        # 设置字体为微软雅黑
        plt.rcParams['font.sans-serif'] = 'Microsoft YaHei'

        # 保存图形到本地文件夹
        plt.savefig(save_path)

        # 显示图形
        plt.show()

    # 从文件中读取数据保存到data
    file_name_base = os.path.basename(file_path)
    file_name = os.path.splitext(file_name_base)[0]
    save_path = r".\image_write\\" + file_name + '.png'
    data = {}
    with open(file_path, "r") as file:
        for line in file:
            defect, count = line.strip().split(": ")
            data[defect] = int(count)

    # 调用可视化函数并保存图表
    visualize_data(data)


# 调用多个函数
def model_detection(fram, model):
    image_data = preprocess_image(fram)
    bbox_data, label_data = detect_image(image_data, model)
    label_data = label_select(label_data)
    return bbox_data, label_data


# 制作视频函数
# 输入四个变量：图片所在文件夹，视频输出位置及文件名(.mp4)，每张图片持续几秒，视频帧率
def images_to_video(input_folder, output_video, duration=3, fps=30):
    # 获取文件夹中所有图片的文件名
    image_files = sorted(os.listdir(input_folder))

    # 读取第一张图片以获取宽度和高度
    first_image_path = os.path.join(input_folder, image_files[0])
    first_image = cv2.imread(first_image_path)
    height, width, _ = first_image.shape

    # 创建视频编码器
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

    # 计算每帧的等待时间
    frame_duration = 1 / fps

    # 计算每张图片应该出现的帧数
    num_images = len(image_files)
    num_frames_per_image = int(duration * fps)

    for image_file in image_files:
        # 读取图片
        image_path = os.path.join(input_folder, image_file)
        image = cv2.imread(image_path)

        # 将当前图片重复添加到视频中
        for _ in range(num_frames_per_image):
            video.write(image)

        # 等待指定的时间
        cv2.waitKey(int(frame_duration * 1000))

    # 释放资源
    video.release()

    print("Video successfully created: " + output_video)

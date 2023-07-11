import tensorflow as tf
from read_data import preprocess_data


def train_model(train_images, train_labels, train_bboxes, model_name, rounds_num):
    # 定义输入层
    image_input = tf.keras.layers.Input(shape=(200, 200, 3))

    # 图像处理部分
    x = tf.keras.layers.Conv2D(32, (3, 3), activation='relu')(image_input)
    x = tf.keras.layers.MaxPooling2D((2, 2))(x)
    x = tf.keras.layers.Conv2D(64, (3, 3), activation='relu')(x)
    x = tf.keras.layers.MaxPooling2D((2, 2))(x)
    x = tf.keras.layers.Conv2D(64, (3, 3), activation='relu')(x)
    x = tf.keras.layers.MaxPooling2D((2, 2))(x)
    x = tf.keras.layers.Conv2D(128, (3, 3), activation='relu')(x)
    x = tf.keras.layers.Flatten()(x)

    # 全连接层部分
    x = tf.keras.layers.Dense(128, activation='relu')(x)

    # 输出层
    bbox_output = tf.keras.layers.Dense(4)(x)
    label_output = tf.keras.layers.Dense(6, activation='softmax')(x)

    # 构建模型
    model = tf.keras.Model(inputs=image_input, outputs=[bbox_output, label_output])

    model.compile(optimizer='adam',
                  loss='mse',
                  metrics=['accuracy'])

    # 训练模型
    model.fit(train_images, [train_bboxes, train_labels], epochs=rounds_num, batch_size=32)

    # 保存模型
    model.save(model_name)


def train_main(xml_folder, image_folder, model_name, rounds_num):
    train_images, test_images, train_labels, test_labels, train_bboxes, test_bboxes = preprocess_data(xml_folder,
                                                                                                      image_folder)
    train_model(train_images, train_labels, train_bboxes, model_name, rounds_num)


if __name__ == '__main__':
    xml_folder = r'./NEU-DET/ANNOTATIONS_test/'
    image_folder = r'./NEU-DET/IMAGES_test/'
    model_name = 'model_3.h5'
    rounds_num = 1
    train_main(xml_folder, image_folder, model_name, rounds_num)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CNN 验证码识别模型模块

基于 TensorFlow/Keras 的 CNN 模型，用于识别登录验证码。
包含模型定义、批量数据加载、训练与预测功能。
"""

import logging
import os
from typing import List, Optional, Tuple

import numpy as np
import tensorflow as tf

import config

logger = logging.getLogger(__name__)

# 字符集常量
NUMBER: List[str] = list("0123456789")
ALPHABET: List[str] = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
CHAR_SET: List[str] = NUMBER + ALPHABET


def build_captcha_model() -> tf.keras.Model:
    """
    构建验证码识别 CNN 模型。

    模型结构：3 组卷积块（每组 2 层 Conv2D + BN + ReLU + MaxPool），
    最终通过 Flatten + Dense 输出 CAPTCHA_SIZE 个字符的分类结果。

    Returns:
        编译前的 Keras 模型
    """
    input_tensor = tf.keras.Input(
        shape=(config.IMAGE_HEIGHT, config.IMAGE_WIDTH, 3)
    )

    x = input_tensor
    for i, num_layers in enumerate([2, 2, 2]):
        for _ in range(num_layers):
            x = tf.keras.layers.Conv2D(
                filters=16 * 2 ** min(i, 3),
                kernel_size=3,
                padding="same",
                activation="relu",
                kernel_initializer="he_uniform",
            )(x)
            x = tf.keras.layers.BatchNormalization()(x)
            x = tf.keras.layers.ReLU()(x)
        x = tf.keras.layers.MaxPool2D((2, 2), strides=2)(x)
        if i in (0, 2):
            x = tf.keras.layers.Dropout(0.2)(x)

    x = tf.keras.layers.Flatten()(x)
    output_tensor = [
        tf.keras.layers.Dense(
            len(CHAR_SET), activation="softmax", name=f"c{i + 1}"
        )(x)
        for i in range(config.CAPTCHA_SIZE)
    ]

    model = tf.keras.Model(input_tensor, output_tensor)
    model.summary()
    return model


class BatchDataLoader:
    """批量加载验证码图片数据，用于模型训练和预测"""

    def __init__(self, char_set: List[str], batch_size: int, captcha_size: int) -> None:
        self.char_set_str = "".join(char_set)
        self.batch_size = batch_size
        self.captcha_size = captcha_size

    def load_batch(
        self, image_dir: str = "./pictemp/"
    ) -> Tuple[np.ndarray, List[np.ndarray]]:
        """
        从指定目录加载一批验证码图片及其标签。

        Args:
            image_dir: 验证码图片所在目录

        Returns:
            (图片数据数组, 标签列表)
        """
        batch_x = np.zeros((self.batch_size, config.IMAGE_HEIGHT, config.IMAGE_WIDTH, 3))
        batch_y = [
            np.zeros((self.batch_size, len(self.char_set_str)), dtype=np.uint8)
            for _ in range(self.captcha_size)
        ]

        images = os.listdir(image_dir)
        for i, image_name in enumerate(images):
            if i >= self.batch_size:
                break

            pic_path = os.path.join(image_dir, image_name)
            raw = tf.io.read_file(pic_path)
            img = tf.image.decode_png(raw, channels=3)
            img = tf.image.convert_image_dtype(img, tf.float64)
            img /= 255.0
            img = tf.reshape(img, (config.IMAGE_HEIGHT, config.IMAGE_WIDTH, 3))
            batch_x[i, :] = img

            filename, _ = os.path.splitext(image_name)
            for j, ch in enumerate(filename):
                batch_y[j][i, :] = 0
                batch_y[j][i, self.char_set_str.index(ch)] = 1

        return batch_x, batch_y

    def vec_to_text(self, vec: np.ndarray) -> str:
        """将模型输出的数值向量转换为文本字符"""
        return "".join(self.char_set_str[item[0]] for item in vec)


class CaptchaTrainer:
    """验证码 CNN 模型训练器"""

    def __init__(
        self,
        model_dir: str,
        batch_size: int,
        char_set: List[str],
        captcha_size: int,
        epochs: int,
    ) -> None:
        self.model = build_captcha_model()
        self.model_dir = model_dir
        self.batch_size = batch_size
        self.char_set = char_set
        self.captcha_size = captcha_size
        self.epochs = epochs

        weights_path = os.path.join(model_dir, "captcha_cnn_best.h5")
        try:
            self.model.load_weights(weights_path)
            self.model.compile(
                optimizer=tf.keras.optimizers.Adam(1e-4, amsgrad=True),
                loss="categorical_crossentropy",
                metrics=["accuracy"],
            )
            logger.info("已加载预训练权重: %s", weights_path)
        except Exception as exc:
            logger.warning("无法加载权重 (%s)，将从头训练", exc)
            self.model.compile(
                optimizer=tf.keras.optimizers.Adam(1e-3, amsgrad=True),
                loss="categorical_crossentropy",
                metrics=["accuracy"],
            )

        self.callbacks = [
            tf.keras.callbacks.EarlyStopping(patience=3),
            tf.keras.callbacks.CSVLogger(
                os.path.join(model_dir, "log", "captcha_cnn.csv"), append=True
            ),
            tf.keras.callbacks.ModelCheckpoint(
                weights_path, save_best_only=True
            ),
        ]

    def train(self) -> None:
        """执行模型训练"""
        train_loader = BatchDataLoader(self.char_set, self.batch_size, self.captcha_size)
        val_loader = BatchDataLoader(self.char_set, 100, self.captcha_size)

        train_x, train_y = train_loader.load_batch()
        val_x, val_y = val_loader.load_batch()

        self.model.fit(
            train_x, train_y,
            epochs=self.epochs,
            validation_data=(val_x, val_y),
            workers=4,
            use_multiprocessing=True,
            callbacks=self.callbacks,
        )
        logger.info("模型训练完成")

    def predict(self) -> None:
        """使用测试数据进行预测并打印结果"""
        test_loader = BatchDataLoader(self.char_set, 1, self.captcha_size)
        data_x, data_y = test_loader.load_batch()

        prediction = self.model.predict(data_x)
        actual = test_loader.vec_to_text(np.argmax(data_y, axis=2))
        predicted = test_loader.vec_to_text(np.argmax(prediction, axis=2))

        if actual.upper() == predicted.upper():
            logger.info("测试数据: %s, 预测数据: %s — 准确", actual, predicted)
        else:
            logger.warning("测试数据: %s, 预测数据: %s — 失败", actual, predicted)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    MODEL_PATH = config.MODEL_DIR
    BATCH_SIZE = 999
    EPOCHS = 1

    trainer = CaptchaTrainer(MODEL_PATH, BATCH_SIZE, CHAR_SET, config.CAPTCHA_SIZE, EPOCHS)
    trainer.train()
    trainer.train()
    trainer.predict()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
乐仁堂口罩预约脚本

通过多进程 + 多线程并发提交预约请求，
使用 CNN 模型自动识别验证码。
"""

import argparse
import datetime
import logging
import multiprocessing
import os
import re
import threading
import time
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import requests
import tensorflow as tf

import config
from cnn.c_cnn import build_captcha_model
from data.basedata import picktime as PICK_TIMES
from data.peopleinfolist import PeopleInfoList
from httpdata.httpheader import get_conn_header, get_pic_header
from httpdata.urlinfo import (
    get_appointment_url,
    get_captcha_url,
    get_form_url,
    get_search_url,
)

logger = logging.getLogger(__name__)


class AppointmentBot:
    """口罩预约自动化机器人"""

    def __init__(
        self,
        urls: Dict[str, str],
        headers: Dict[str, Dict[str, str]],
        people_list: List[Dict[str, str]],
        pick_times: List[str],
    ) -> None:
        """
        初始化预约机器人。

        Args:
            urls: 各接口 URL 字典
            headers: HTTP 请求头字典
            people_list: 人员信息列表
            pick_times: 预约时段列表
        """
        self.appointment_url = urls["appointment"]
        self.result_url = urls["result"]
        self.captcha_url = urls["captcha"]
        self.form_url = urls["form"]

        self.conn_header = headers["conn_header"]
        self.pic_header = headers["pic_header"]

        self.process_count = config.PROCESS_COUNT
        self.thread_count = config.THREAD_COUNT

        self.appointment_list = self._build_appointment_list(people_list, pick_times)
        self.query_list = self._build_query_list(people_list)

        # 加载验证码识别模型
        self.model = build_captcha_model()
        self.model.load_weights(config.MODEL_WEIGHTS_PATH)
        self.char_set = config.CHAR_SET
        logger.info("验证码识别模型加载完成")

    def _build_appointment_list(
        self,
        people_list: List[Dict[str, str]],
        pick_times: List[str],
    ) -> List[Dict[str, str]]:
        """
        构建预约信息列表。

        将人员信息与所有可用时段组合，确保每人可尝试预约当天全部时段。

        Args:
            people_list: 人员信息列表
            pick_times: 预约时段列表

        Returns:
            格式化后的预约信息列表
        """
        # 获取明日日期作为预约日期
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        appo_date = tomorrow.strftime("%Y-%m-%d")

        result: List[Dict[str, str]] = []
        for time_slot in pick_times:
            for person in people_list:
                appo_info = {
                    "realname": person["name"],
                    "phone": person["phone"],
                    "shenfenzheng": person["id"],
                    "area": person["areaid"],
                    "shop": person["shopid"],
                    "pickdate": appo_date,
                    "shuliang": "5",
                    "pid": "1",
                    "yzm": "",
                    "token": "",
                    "picktime": time_slot,
                }
                result.append(appo_info)

        logger.info(
            "已构建 %d 条预约信息（%d 人 × %d 时段）",
            len(result), len(people_list), len(pick_times),
        )
        return result

    def _build_query_list(
        self, people_list: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """构建预约结果查询列表"""
        return [
            {
                "realname": person["name"],
                "shenfenzheng": person["id"],
                "pid": "1",
                "result": "",
            }
            for person in people_list
        ]

    def run(self) -> None:
        """
        启动多进程预约。

        创建进程池，将数据列表拆分后分配给各进程处理。
        """
        pool = multiprocessing.Pool(self.process_count)
        chunk_size = len(self.appointment_list) // self.process_count + 1
        chunks = list(self._split_list(self.appointment_list, chunk_size))

        logger.info(
            "启动 %d 个进程，每进程处理约 %d 条数据",
            len(chunks), chunk_size,
        )

        for chunk in chunks:
            pool.apply_async(self._thread_dispatch, args=(chunk, self.appointment_url))

        pool.close()
        pool.join()
        logger.info("本轮预约完成")

    @staticmethod
    def _split_list(data: list, chunk_size: int):
        """按固定步长拆分列表"""
        for i in range(0, len(data), chunk_size):
            yield data[i : i + chunk_size]

    def _thread_dispatch(self, data_list: list, url: str) -> None:
        """
        在进程内创建多线程处理预约请求。

        Args:
            data_list: 待处理的预约信息列表
            url: 预约提交 URL
        """
        chunk_size = len(data_list) // self.thread_count + 1
        chunks = list(self._split_list(data_list, chunk_size))
        threads: List[threading.Thread] = []

        for chunk in chunks:
            thread = threading.Thread(target=self._submit_appointments, args=(url, chunk))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

    def _submit_appointments(self, url: str, info_list: list) -> None:
        """
        向服务器发送 POST 请求完成预约。

        流程：获取 cookies/token → 下载验证码 → CNN 识别 → 提交表单

        Args:
            url: 预约提交 URL
            info_list: 预约信息列表
        """
        headers = {
            "header": self.conn_header.copy(),
            "pic_header": self.pic_header.copy(),
        }

        for item in info_list:
            try:
                # 获取实时 cookies 和 token
                updated_headers, token = self._fetch_cookies_and_token(headers)
                # 下载验证码图片
                pic_path = self._download_captcha(
                    updated_headers["pic_header"], item["phone"]
                )
                # 识别验证码
                item["yzm"] = str(self._recognize_captcha(pic_path))
                item["token"] = token

                response = requests.post(
                    url, data=item.copy(), headers=updated_headers["pic_header"]
                )
                logger.info("预约响应: %s", response.json())

            except ConnectionResetError:
                logger.warning("连接被重置，短暂等待后重试")
                time.sleep(0.01)
            except Exception as exc:
                logger.error("预约提交异常: %s", exc)

    def query_results(self) -> None:
        """查询预约结果并保存到文件"""
        os.makedirs(config.RESULT_DIR, exist_ok=True)
        result_path = os.path.join(config.RESULT_DIR, "result.txt")

        with open(result_path, "w", encoding="utf-8") as f:
            for item in self.query_list:
                response = requests.post(
                    self.result_url, data=item, headers=self.conn_header
                )
                f.write(str(response.json()) + "\n")

        logger.info("查询结果已保存至: %s", result_path)

    def _fetch_cookies_and_token(
        self, headers: Dict[str, Dict[str, str]]
    ) -> Tuple[Dict[str, Dict[str, str]], str]:
        """
        从表单页面获取 cookies 和 token。

        Returns:
            (更新后的 headers, token 值)
        """
        try:
            response = requests.get(url=self.form_url)
            while response.status_code != 200:
                try:
                    response = requests.get(url=self.form_url)
                except Exception as exc:
                    logger.error("获取表单页面失败: %s", exc)
        except Exception as exc:
            logger.error("请求表单页面异常: %s", exc)
            raise

        # 从页面中提取 token
        pattern = re.compile(r"var token = \S+';")
        match = pattern.search(response.text)
        token = match.group(0).split("'")[1] if match else ""

        # 更新 cookies
        cookies = requests.utils.dict_from_cookiejar(response.cookies)
        for key, value in cookies.items():
            cookie_str = f"{key}={value}"
            headers["header"]["Cookie"] = cookie_str
            headers["pic_header"]["Cookie"] = cookie_str

        return headers, token

    def _download_captcha(self, header: dict, filename: str) -> str:
        """
        下载验证码图片。

        Args:
            header: HTTP 请求头
            filename: 保存文件名（不含扩展名）

        Returns:
            保存后的文件路径
        """
        try:
            response = requests.get(self.captcha_url, headers=header)
            while response.status_code != 200:
                try:
                    response = requests.get(self.captcha_url, headers=header)
                except Exception as exc:
                    logger.error("获取验证码失败: %s", exc)
        except Exception as exc:
            logger.error("请求验证码异常: %s", exc)
            raise

        pic_path = os.path.join(config.CAPTCHA_TEMP_DIR, f"{filename}.png")
        with open(pic_path, "wb") as f:
            f.write(response.content)

        return pic_path

    def _recognize_captcha(self, pic_path: str) -> str:
        """
        使用 CNN 模型识别验证码。

        注意：模型训练数据有限（999 条），识别准确率受限。

        Args:
            pic_path: 验证码图片路径

        Returns:
            识别出的验证码文本
        """
        data_x = np.zeros((1, config.IMAGE_HEIGHT, config.IMAGE_WIDTH, 3))
        raw = tf.io.read_file(pic_path)
        img = tf.image.decode_png(raw, channels=3)
        img = tf.image.convert_image_dtype(img, tf.float64)
        img /= 255.0
        img = tf.reshape(img, (config.IMAGE_HEIGHT, config.IMAGE_WIDTH, 3))

        data_x[0, :] = img
        prediction = self.model.predict(data_x)
        result = "".join(
            self.char_set[item[0]] for item in np.argmax(prediction, axis=2)
        )
        return result


def main() -> None:
    """主入口函数"""
    parser = argparse.ArgumentParser(description="乐仁堂口罩预约脚本")
    parser.add_argument(
        "-n", "--count",
        type=int,
        default=config.DEFAULT_PEOPLE_COUNT,
        help=f"随机生成的预约人数（默认: {config.DEFAULT_PEOPLE_COUNT}）",
    )
    parser.add_argument(
        "--query",
        action="store_true",
        help="仅查询预约结果",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="显示详细日志",
    )
    args = parser.parse_args()

    # 配置日志
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 构建 URL 和 Header 配置
    urls = {
        "appointment": get_appointment_url(),
        "result": get_search_url(),
        "captcha": get_captcha_url(),
        "form": get_form_url(),
    }
    headers = {
        "conn_header": get_conn_header(),
        "pic_header": get_pic_header(),
    }

    # 生成随机人员信息
    people_generator = PeopleInfoList(args.count)
    people_list = people_generator.get_people_list()

    # 创建预约机器人
    bot = AppointmentBot(urls, headers, people_list, PICK_TIMES)

    if args.query:
        bot.query_results()
        return

    # 保存本次生成的身份信息（方便后续查询预约结果）
    os.makedirs(config.INFO_LIST_DIR, exist_ok=True)
    info_file = os.path.join(
        config.INFO_LIST_DIR, f"{time.time()}_plist.txt"
    )
    with open(info_file, "w", encoding="utf-8") as f:
        for person in people_list:
            f.write(str(person) + "\n")
    logger.info("人员信息已保存至: %s", info_file)

    # 设置停止时间
    stop_time_str = (
        datetime.date.today().strftime("%Y-%m-%d") + f" {config.STOP_TIME}"
    )
    stop_timestamp = time.mktime(
        time.strptime(stop_time_str, "%Y-%m-%d %H:%M:%S")
    )
    logger.info("预约将在 %s 停止", stop_time_str)

    # 持续预约直到停止时间
    round_count = 0
    while time.time() < stop_timestamp:
        round_count += 1
        logger.info("========== 第 %d 轮预约开始 ==========", round_count)
        bot.run()

    logger.info("预约已结束，共执行 %d 轮", round_count)


if __name__ == "__main__":
    main()

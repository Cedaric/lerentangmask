#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
验证码图片下载工具

从服务器获取验证码图片并保存到本地临时目录。
"""

import logging
import time
from typing import Optional

import requests

import config

logger = logging.getLogger(__name__)


class CaptchaDownloader:
    """验证码图片下载器"""

    def __init__(self, captcha_url: Optional[str] = None) -> None:
        """
        Args:
            captcha_url: 验证码接口 URL，默认使用 config 中的配置
        """
        self.captcha_url = captcha_url or config.CAPTCHA_URL

    def download(self, header: dict, filename: str) -> str:
        """
        下载验证码图片并保存到本地。

        Args:
            header: HTTP 请求头
            filename: 保存的文件名（不含扩展名）

        Returns:
            保存后的文件路径
        """
        try:
            response = requests.get(self.captcha_url, headers=header)
            while response.status_code != 200:
                try:
                    response = requests.get(self.captcha_url, headers=header)
                    time.sleep(0.5)
                except Exception as exc:
                    logger.error("获取验证码失败: %s", exc)
                    time.sleep(1)
        except Exception as exc:
            logger.error("请求验证码异常: %s", exc)
            raise

        pic_path = f"{config.CAPTCHA_TEMP_DIR}{filename}.png"
        with open(pic_path, "wb") as f:
            f.write(response.content)

        logger.debug("验证码已保存: %s", pic_path)
        return pic_path


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    header = config.PIC_HEADER.copy()
    downloader = CaptchaDownloader()

    for i in range(1000):
        downloader.download(header, str(i))
        if i % 100 == 0:
            logger.info("已下载 %d 张验证码", i + 1)
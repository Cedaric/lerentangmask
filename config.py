#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
集中配置管理模块

将所有硬编码的配置参数统一管理，包括 URL、HTTP 请求头、
预约时段、CNN 模型参数等。
"""

import multiprocessing
from typing import Dict, List


# ========== URL 配置 ==========

APPOINTMENT_URL: str = "http://lerentang.yihecm.com/?m=save"
SEARCH_URL: str = "http://lerentang.yihecm.com/?m=resultchaxun"
CAPTCHA_URL: str = "http://lerentang.yihecm.com/core/common/yzm.php?0.29450912268882457"
FORM_URL: str = "http://lerentang.yihecm.com/?m=yuyuelist&id=1"


# ========== HTTP 请求头 ==========

_COMMON_HEADERS: Dict[str, str] = {
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-cn",
    "Connection": "close",
    "Host": "lerentang.yihecm.com",
    "User-Agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 13_3_1 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 "
        "MicroMessenger/7.0.10(0x17000a21) NetType/WIFI Language/zh_CN"
    ),
}

# 提交预约使用的头部信息
CONN_HEADER: Dict[str, str] = {
    **_COMMON_HEADERS,
    "Accept": "*/*",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Cookie": "PSESSID=fkg7p3icjjs80sjq1k1484mdg4",
    "Origin": "http://lerentang.yihecm.com",
    "Referer": "http://lerentang.yihecm.com/?m=yuyuelist&id=1",
    "X-Requested-With": "XMLHttpRequest",
}

# 下载验证码使用的头部信息（cookies 会实时更换）
PIC_HEADER: Dict[str, str] = {
    **_COMMON_HEADERS,
    "Accept": "image/png,image/svg+xml,image/*;q=0.8,video/*;q=0.8,*/*;q=0.5",
    "Cookie": "PHPSESSID=fkg7p3icjjs80sjq1k1484mdg4",
    "Referer": "http://lerentang.yihecm.com/?m=yuyuelist&id=1",
}

# 获取 cookies 使用的头部信息
DEFAULT_HEADER: Dict[str, str] = {
    **_COMMON_HEADERS,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Cookie": "PHPSESSID=frmecrb4vsc7g1pf12f81qcej1",
    "Referer": "http://lerentang.yihecm.com/?m=list",
    "Upgrade-Insecure-Requests": "1",
}


# ========== 预约配置 ==========

# 预约时段
PICK_TIMES: List[str] = [
    "09:00-11:00",
    "11:00-13:00",
    "13:00-15:00",
    "15:00-17:00",
    "17:00-19:00",
]

# 默认预约人数
DEFAULT_PEOPLE_COUNT: int = 50

# 每日停止预约时间（HH:MM:SS）
STOP_TIME: str = "19:45:30"


# ========== CNN 模型配置 ==========

MODEL_WEIGHTS_PATH: str = "./cnn/keras_cnn/captcha_cnn_best.h5"
MODEL_DIR: str = "./cnn/keras_cnn/"
CHAR_SET: str = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
CAPTCHA_SIZE: int = 4
IMAGE_HEIGHT: int = 25
IMAGE_WIDTH: int = 80


# ========== 并发配置 ==========

CPU_COUNT: int = multiprocessing.cpu_count()
PROCESS_COUNT: int = int(CPU_COUNT / 2 + 1)
THREAD_COUNT: int = int(CPU_COUNT + 1)


# ========== 文件路径 ==========

CAPTCHA_TEMP_DIR: str = "./data/pictemp/"
RESULT_DIR: str = "./result/"
INFO_LIST_DIR: str = "./data/infolist/"

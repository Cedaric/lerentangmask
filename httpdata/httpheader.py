#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HTTP 请求头管理模块

提供不同场景下的 HTTP 请求头配置。
"""

from typing import Dict

import config


def get_conn_header() -> Dict[str, str]:
    """获取提交预约使用的请求头"""
    return config.CONN_HEADER.copy()


def get_pic_header() -> Dict[str, str]:
    """获取下载验证码使用的请求头（cookies 会实时更换）"""
    return config.PIC_HEADER.copy()


def get_default_header() -> Dict[str, str]:
    """获取用于获取 cookies 的请求头"""
    return config.DEFAULT_HEADER.copy()
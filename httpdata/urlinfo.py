#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
URL 配置管理模块

提供各接口 URL 的访问方法。
"""

import config


def get_appointment_url() -> str:
    """获取预约提交 URL"""
    return config.APPOINTMENT_URL


def get_search_url() -> str:
    """获取预约结果查询 URL"""
    return config.SEARCH_URL


def get_captcha_url() -> str:
    """获取验证码图片 URL"""
    return config.CAPTCHA_URL


def get_form_url() -> str:
    """获取预约表单页面 URL"""
    return config.FORM_URL
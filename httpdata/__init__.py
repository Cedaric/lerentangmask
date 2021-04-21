#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""httpdata 包 — HTTP 请求相关工具"""

from httpdata.httpheader import get_conn_header, get_pic_header, get_default_header
from httpdata.urlinfo import (
    get_appointment_url,
    get_search_url,
    get_captcha_url,
    get_form_url,
)

__all__ = [
    "get_conn_header",
    "get_pic_header",
    "get_default_header",
    "get_appointment_url",
    "get_search_url",
    "get_captcha_url",
    "get_form_url",
]
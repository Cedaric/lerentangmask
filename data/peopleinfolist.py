#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
随机人员信息生成模块

生成随机的人员信息（姓名、身份证号、手机号、门店），
用于批量提交预约请求。
"""

import logging
import random
import threading
from typing import Dict, List, Set

logger = logging.getLogger(__name__)


class PeopleInfoList:
    """随机生成指定数量的人员信息列表"""

    # 姓氏库
    FIRST_NAMES: List[str] = [
        "张", "白", "林", "杨", "刘", "梁", "苏", "石", "赛", "尚", "丁", "董", "王",
        "戴", "段", "方", "范", "冯", "高", "郭", "许", "徐", "聂", "黄", "赵", "周",
        "章", "陈", "曾", "牛", "朱", "钟", "韩", "包", "吕", "展", "魏", "金", "童",
        "顾", "孙", "郑", "胡", "邓", "左", "靳", "闻", "葛", "司", "田", "吴", "马",
        "卞", "崔", "甄", "曹", "杜", "郝", "毛", "任", "潘", "谢", "姜", "武",
        "袁", "尹", "于", "何", "叶", "薛", "要", "宁", "耿", "司马", "上官", "欧阳",
        "次", "冉", "艾", "诸葛", "孔", "夏", "沙", "齐", "江", "贾", "连", "秦",
        "侯", "孟", "卢", "邵", "蔡", "程", "万", "姚", "罗", "韦", "唐", "朗",
        "贺", "沈", "汤", "佟", "慕", "闫", "谭", "陆", "祁", "丰", "古", "娄", "洪",
    ]

    # 名字字库
    LAST_NAMES: List[str] = [
        "水", "静", "敏", "聪", "辉", "慧", "淼", "永", "国", "刚", "强", "风", "花",
        "雪", "月", "涛", "海", "萍", "晶", "丽", "利", "峰", "明", "星", "兴", "乐",
        "龙", "旺", "易", "婉", "楠", "笑", "霞", "光", "彩", "才", "益", "帅", "琳",
        "晓", "雅", "俊", "军", "赫", "凯", "耀", "杰", "芳", "航", "达", "垣", "屹",
        "珊", "姗", "彬", "斌", "秀", "玲", "松", "铭", "洲", "亚", "叶", "文",
        "娟", "玉", "婷", "博", "礼", "莉", "莹", "梦", "英", "雄", "珑", "烟", "泰",
        "晨", "志", "智", "珉", "烨", "贤", "阳", "洋", "安", "康", "翔", "丰",
        "飞", "伟", "威", "薇", "娜", "冰", "霜", "浅", "清", "琴", "勤", "亮", "晴",
        "青", "庆", "柳", "秋", "语", "荣", "念", "缘", "羽", "柔", "婕",
        "杉", "缤", "梅", "彤", "盛", "硕", "琼", "宁", "豪", "华", "欣", "坤", "璐",
        "襄", "超", "川", "宇", "柏", "贝", "慈", "睿", "瑞", "祥", "树", "兰", "岚",
        "旭", "芝", "诺", "佳", "嘉", "雨", "天", "鸿", "航", "澜", "忠",
        "富", "福", "悦", "越", "艺", "栋", "毅", "歌", "芬", "浩",
        "腾", "鑫", "蕾", "雷", "帆", "鹏", "桃", "舟", "茜", "策", "露",
        "欢", "心", "一", "初", "涵", "然", "璇", "颖", "蓬", "娥", "琪", "琦",
        "新", "淑", "君", "娇", "莎", "倩", "窈", "窕", "茗", "恒", "萱", "珍",
        "昭", "朝", "宝", "萌", "楚", "瑛", "滢", "菲", "翠", "远", "云", "韵", "运",
        "浮", "笙", "仙", "世", "和", "碧", "靖", "菁", "宗", "剑", "河", "谨",
        "义", "彦", "家", "辰", "舒", "香", "茹", "柯", "德", "燕", "影", "敬",
        "景", "雯", "磊",
    ]

    # 手机号段前缀
    PHONE_SEGMENTS: List[str] = [
        "136", "139", "151", "133", "156", "155", "130", "177",
        "173", "172", "188", "178", "132", "180", "150", "189",
        "185", "186", "137", "159", "131",
    ]

    # 石家庄地区行政区划代码
    PLACE_CODES: List[str] = [
        "130102", "130104", "130105", "130107",
        "130108", "130109", "130110",
    ]

    # 门店与区域信息
    SHOPS: List[Dict[str, str]] = [
        {"shopid": "15", "areaid": "3"},
        {"shopid": "18", "areaid": "15"},
        {"shopid": "20", "areaid": "15"},
        {"shopid": "23", "areaid": "15"},
        {"shopid": "36", "areaid": "15"},
        {"shopid": "37", "areaid": "15"},
        {"shopid": "38", "areaid": "15"},
        {"shopid": "50", "areaid": "15"},
        {"shopid": "60", "areaid": "15"},
    ]

    # 身份证号校验码权重
    ID_WEIGHTS: List[int] = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    ID_CHECK_CODES: Dict[int, str] = {
        0: "1", 1: "0", 2: "X", 3: "9", 4: "8",
        5: "7", 6: "6", 7: "5", 8: "4", 9: "3", 10: "2",
    }

    def __init__(self, count: int) -> None:
        """
        初始化并生成指定数量的随机人员信息。

        Args:
            count: 需要生成的人员数量
        """
        self.count = count
        self._id_list: List[str] = []
        self._name_list: List[str] = []
        self._phone_list: List[str] = []
        self._shop_list: List[Dict[str, str]] = []
        self._people_info_list: List[Dict[str, str]] = []

        # 使用多线程并行生成各类随机数据
        threads = [
            threading.Thread(target=self._generate_ids),
            threading.Thread(target=self._generate_names),
            threading.Thread(target=self._generate_phones),
            threading.Thread(target=self._generate_shops),
        ]

        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        self._build_people_info_list()
        logger.info("已生成 %d 条随机人员信息", self.count)

    def _generate_ids(self) -> None:
        """生成随机身份证号码（仅限日期 1-28 日，避免月份天数差异）"""
        ids: Set[str] = set()

        while len(ids) < self.count:
            place_code = random.choice(self.PLACE_CODES)
            year = str(random.randint(1963, 2011))
            month = random.randint(1, 12)
            day = random.randint(1, 28)
            date_str = f"{year}{month:02d}{day:02d}"
            order_code = str(random.randint(100, 999))

            id_body = place_code + date_str + order_code

            # 计算校验码
            checksum = sum(
                int(ch) * w for ch, w in zip(id_body, self.ID_WEIGHTS)
            )
            check_code = self.ID_CHECK_CODES[checksum % 11]
            ids.add(id_body + check_code)

        self._id_list = list(ids)

    def _generate_names(self) -> None:
        """随机生成人员姓名（姓 + 两个名字字符）"""
        names: Set[str] = set()

        while len(names) < self.count:
            name = (
                random.choice(self.FIRST_NAMES)
                + random.choice(self.LAST_NAMES)
                + random.choice(self.LAST_NAMES)
            )
            if len(name) > 1:
                names.add(name)

        self._name_list = list(names)

    def _generate_phones(self) -> None:
        """生成随机手机号"""
        phones: Set[str] = set()

        while len(phones) < self.count:
            segment = random.choice(self.PHONE_SEGMENTS)
            suffix = str(random.randint(32567112, 99998698))
            phones.add(segment + suffix)

        self._phone_list = list(phones)

    def _generate_shops(self) -> None:
        """随机分配门店及区域信息"""
        self._shop_list = [
            random.choice(self.SHOPS).copy()
            for _ in range(self.count)
        ]

    def _build_people_info_list(self) -> None:
        """组装完整的人员信息列表"""
        for i, shop_info in enumerate(self._shop_list):
            person = {
                **shop_info,
                "phone": self._phone_list[i],
                "name": self._name_list[i],
                "id": self._id_list[i],
                "yzm": "",
            }
            self._people_info_list.append(person)

    def get_people_list(self) -> List[Dict[str, str]]:
        """返回生成的人员信息列表"""
        return self._people_info_list

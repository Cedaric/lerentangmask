# 🏥 LeRenTang Mask — 乐仁堂口罩预约脚本

> 2020 年新冠疫情期间针对河北乐仁堂药房口罩预约系统的自动化脚本。

## 📋 项目简介

本项目诞生于 2020 年 2 月新冠疫情早期，口罩供应紧张。[乐仁堂药房](http://lerentang.yihecm.com/) 提供了线上口罩预约系统，但名额有限、手动预约难以成功。本脚本通过自动化手段批量提交预约请求，提高预约成功率。

### 核心功能

- 🤖 **自动化预约**：多进程 + 多线程并发提交，最大化预约成功率
- 🔍 **验证码识别**：基于 TensorFlow/Keras 的 CNN 模型自动识别登录验证码
- 👤 **随机身份生成**：自动生成符合规则的随机人员信息（姓名、身份证号、手机号）
- 📊 **结果查询**：支持批量查询预约结果并保存

## 🏗️ 技术架构

```
┌─────────────────────────────────────────────────────────┐
│                    appointment.py                        │
│              主入口 / 预约调度 / 并发控制                  │
│         (多进程 Pool + 多线程 Thread 并发提交)             │
├──────────┬──────────────┬───────────────┬────────────────┤
│ config   │   httpdata/  │    data/      │     cnn/       │
│ 集中配置  │  HTTP 请求管理 │ 数据生成      │  验证码识别     │
│          │  · 请求头模板  │ · 随机身份信息  │ · CNN 模型定义  │
│          │  · URL 配置   │ · 门店/时段    │ · 模型训练      │
│          │              │              │ · 验证码下载     │
└──────────┴──────────────┴───────────────┴────────────────┘
```

## 📁 目录结构

```
LeRenTang_Mask/
├── appointment.py          # 主入口脚本
├── config.py               # 集中配置管理
├── requirements.txt        # Python 依赖
├── .gitignore              # Git 忽略规则
├── LICENSE                 # Apache License 2.0
│
├── cnn/                    # CNN 验证码识别模块
│   ├── c_cnn.py            #   模型定义 / 训练 / 预测
│   ├── getpic.py           #   验证码图片下载工具
│   ├── keras_cnn/          #   Keras 模型权重文件
│   │   └── captcha_cnn_best.h5
│   └── pictemp/            #   验证码临时图片（训练用）
│
├── data/                   # 数据模块
│   ├── basedata.py         #   基础配置（预约时段等）
│   ├── peopleinfolist.py   #   随机人员信息生成器
│   ├── pictemp/            #   验证码临时图片（运行时）
│   └── infolist/           #   已生成的身份信息记录
│
├── httpdata/               # HTTP 请求模块
│   ├── httpheader.py       #   请求头管理
│   └── urlinfo.py          #   URL 配置
│
├── pages/                  # 归档
│   └── 2020-02-22.html     #   预约页面快照
│
└── result/                 # 预约结果输出
```

## ⚙️ 安装

### 前置要求

- Python 3.7+
- pip

### 安装依赖

```bash
git clone https://github.com/Cedaric/LeRenTang_Mask.git
cd LeRenTang_Mask
pip install -r requirements.txt
```

## 🚀 使用方法

### 基本用法

```bash
# 默认随机生成 50 人信息并持续预约至 19:45
python appointment.py

# 指定预约人数
python appointment.py -n 100

# 查询预约结果
python appointment.py --query

# 显示详细日志
python appointment.py -v
```

### 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `-n, --count` | 随机生成的预约人数 | 50 |
| `--query` | 仅查询预约结果 | - |
| `-v, --verbose` | 显示详细调试日志 | - |

### 配置说明

所有配置项集中在 `config.py` 中管理：

| 配置项 | 说明 |
|--------|------|
| `APPOINTMENT_URL` | 预约提交接口 |
| `CAPTCHA_URL` | 验证码获取接口 |
| `PICK_TIMES` | 可预约时段列表 |
| `DEFAULT_PEOPLE_COUNT` | 默认生成人数 |
| `STOP_TIME` | 每日停止预约时间 |
| `MODEL_WEIGHTS_PATH` | CNN 模型权重路径 |
| `PROCESS_COUNT` / `THREAD_COUNT` | 并发数（基于 CPU 核数自动计算） |

## 🧠 验证码识别

使用 CNN（卷积神经网络）模型识别 4 位字母数字混合验证码：

- **字符集**：`0-9` + `A-Z`（共 36 类）
- **模型结构**：3 组卷积块（Conv2D + BatchNorm + ReLU + MaxPool + Dropout）
- **训练数据**：约 999 张标注验证码图片
- **图片尺寸**：25 × 80 像素

> ⚠️ **注意**：由于训练集较小，识别准确率有限。如需提高准确率，可通过 `cnn/getpic.py` 下载更多验证码图片，手动标注后重新训练模型。

### 训练模型

```bash
cd cnn
python c_cnn.py
```

## ⚠️ 免责声明

- 本项目仅用于学习和研究自动化技术，**不鼓励用于任何商业或违规用途**
- 预约系统（`lerentang.yihecm.com`）已于疫情后下线，本脚本**无法实际运行**
- 项目中如有残留的个人信息均为随机生成，不涉及真实个人数据

## 📄 许可证

[Apache License 2.0](./LICENSE)

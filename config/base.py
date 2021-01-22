# -*- coding: utf-8 -*-
import os


class BaseConfig(object):
    """配置基类"""

    TIMEZONE = "Asia/Shanghai"  # 时区设置

    # 项目根目录地址
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # DEBUG模式
    DEBUG = False

    TRY_TIMES = 5  # 加密次数
    SALT_ARRAY = ["QMTbsB5E9hvHaAGt",
                  "hWtaqm9HJ5SDyM8A",
                  "3fHYMNOshXapES2BnLov4r7C",
                  "ew2pymSFabzLRdA98uvV36457hD1oq0f",
                  "7M6yxojXZ5FHdQlsG31qPeIApONVDhC9t2YnuUrkmR"]  # 用于加盐的数组

    # 关闭，否则影响server性能
    ACCESS_LOG = False

    # 服务worker数量
    WORKERS = 1

    # 跨域相关
    ENABLE_CORS = False  # 是否启动跨域功能
    CORS_SUPPORTS_CREDENTIALS = True

    DATABASE = {
        "DATABASE_TYPE": "mysql",
        "HOST": "10.244.201.161",
        "PORT": 3306,
        "USER": "root",
        "PASSWORD": "#EDC4rfv5tgb",
        "DB": "sanic_demo",
        "CHARSET": "utf8"
    }

    # redis
    # db0: 存储发送手机验证码所用
    # db1: 用户存储用户Token所用
    # 请勿切换错误
    REDIS = {
        "address": ("127.0.0.1", 6379),
        "password": "123456",
        # 'ssl': None,
        # 'encoding': None,
        # 'minsize': 1,
        # 'maxsize': 10
    }

    MKDIR_LOGS = os.path.join(BASE_DIR, "logs")

    # 日志配置，兼容 sanic内置log库
    LOGGING_INFO_FILE = os.path.join(MKDIR_LOGS, "info.log")
    LOGGING_ERROR_FILE = os.path.join(MKDIR_LOGS, "error.log")
    BASE_LOGGING = {
        'version': 1,
        'loggers': {
            "sanic.root": {"level": "INFO", "handlers": ["console", 'info_file', 'error_file']},
        },
        'formatters': {
            'default': {
                'format': '%(asctime)s | %(levelname)s | %(message)s',
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'INFO',
                'formatter': 'default',
            },
            'info_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': LOGGING_INFO_FILE,
                'maxBytes': (1 * 1024 * 1024),
                'backupCount': 10,
                'encoding': 'utf8',
                'level': 'INFO',
                'formatter': 'default',
            },
            'error_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': LOGGING_ERROR_FILE,
                'maxBytes': (1 * 1024 * 1024),
                'backupCount': 10,
                'encoding': 'utf8',
                'level': 'ERROR',
                'formatter': 'default',
            },
        },
    }

    def __init__(self):
        if not os.path.exists(self.MKDIR_LOGS):  # 如果不存在logs文件夹就创建
            os.mkdir(self.MKDIR_LOGS)
            file_1 = open(self.LOGGING_INFO_FILE, mode="a", encoding="utf-8")  # 创建日志文件
            file_2 = open(self.LOGGING_ERROR_FILE, mode="a", encoding="utf-8")
            file_1.close()
            file_2.close()

        if self.LOGGING_INFO_FILE:
            self.BASE_LOGGING['handlers']['info_file']['filename'] = self.LOGGING_INFO_FILE

        if self.LOGGING_ERROR_FILE:
            self.BASE_LOGGING['handlers']['error_file']['filename'] = self.LOGGING_ERROR_FILE

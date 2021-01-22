# -*- coding: utf-8 -*-
"""
Usage:
配置类 模块
"""
from config.base import BaseConfig
from config.develop import DevelopConfig
from config.product import ProductConfig
from config.local import LocalConfig
import os


ConfigMap = {
    'LOCAL': LocalConfig,  # 本地开发者环境
    'DEV': DevelopConfig,  # 线上测试库环境
    'PROD': ProductConfig  # 线上生产环境
}

# 设置环境变量
SANIC_ENV = os.environ.get('SANIC_ENV', 'LOCAL')


def get_config(env=None) -> BaseConfig:
    if not env:
        # 获取环境变量, 默认使用本地环境
        env = SANIC_ENV
    env = env.upper()

    config_cls = ConfigMap.get(env)
    if not config_cls:
        raise EnvironmentError(
            '环境配置错误, 默认使用 LOCAL 环境, 需要 config/local.py 文件.'
            '若要切换其他环境的配置, 需设置环境变量, 如 SANIC_ENV=TEST.')
    return config_cls()

# -*- coding: utf-8 -*-
from .base import BaseConfig


class ProductConfig(BaseConfig):
    """生产环境配置"""

    WORKERS = 4

# -*- coding: utf-8 -*-
"""
Module usage:
各种中间件
"""
from .log import LogMiddleware

MIDDLEWARE = [LogMiddleware]

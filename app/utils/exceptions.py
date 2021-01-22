# -*- coding: utf-8 -*-
from sqlalchemy.exc import IntegrityError


class ApiException(Exception):
    """项目的API处理时的基础异常"""

    def __init__(self, code=500, message=None):
        super().__init__(message)
        self.code = code
        self.message = message


class DataBaseError(Exception):
    """数据库相关异常捕获"""



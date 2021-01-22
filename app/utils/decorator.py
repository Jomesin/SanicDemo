#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: JISO
# Email: 747142549@qq.com
# File: decorator.py
from functools import wraps
from app.utils.messages import CodeDict


def judge_request_json(return_data_dict, response):
    """
    判断request.json中的数据是否为空的装饰器
    :param return_data_dict: 要判断request.json中哪些数据,返回message和状态码
    :param response: 返回响应对象,只能为本系统封装的return_json对象
    :return: response(响应对象)
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(request, *args):
            data = request.json  # 获取请求体数据
            if isinstance(data, dict):  # 判断请求体数据是否为键值对字典结构
                if data is None or not data:  # 如果数据是None或者为空
                    return response(message=CodeDict.DATA_EMPTY[0], status_code=CodeDict.DATA_EMPTY[1])

                for data_key, return_tuple in return_data_dict.items():
                    if data.get(data_key, None) is None:  # 判断数据是否为空
                        # 返回响应
                        return response(message=return_tuple[0], status_code=return_tuple[1])
            # 回调视图函数
            res = await func(request, *args)
            return res
        return wrapper
    return decorator

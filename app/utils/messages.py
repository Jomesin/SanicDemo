# -*- coding: utf-8 -*-


class CodeDict(object):
    """内部公共错误状态码"""

    DATA_EMPTY = (100, "请求数据不能为空!")  # POST请求中request.json不能为空!
    SUCCESS = (200, "OK!")
    NOT_FOUND = (404, "找不到相关资源!")
    METHOD_BOT_ALLOW = (405, "方法不被允许!")
    FAIL = (500, "服务器内部错误!")

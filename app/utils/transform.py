# -*- coding: utf-8 -*-
import uuid


def str2byte(_str):
    """
    str to bytes
    :param _str:
    :return:
    """
    return bytes(_str, encoding='utf-8')


def byte2str(_bytes):
    """
    bytes to str
    :param _str:
    :return:
    """
    return str(_bytes, encoding="utf-8")

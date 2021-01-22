# -*- coding: utf-8 -*-
from sanic import response


class DataInfo(object):
    """数据主体部分"""

    def __new__(cls, list_data=None, page_info=None):
        if isinstance(list_data, list):
            assert page_info, "如果数据为数组时必须要有分页信息"

        return {
            "list_data": list_data,  # 数据数组 or 数据字典
            "page_info": page_info  # 如果list_data是
        }


class PageInfo(object):
    """分页所用的返回数据结构"""

    def __new__(cls, current_page_number=1, page_size=20, total_size=0):
        """
        :param current_page_number: 当前页码
        :param page_size: 每页多少数据
        :param total_size: 总共数据量
        """

        total_size = int(total_size)
        page_size = int(page_size)

        if page_size is 0:
            page_size = 1

        if total_size % page_size == 0:  # 如果总数据条数 求余运算 每页数据条数等于的话,就证明是倍数
            total_page = total_size // page_size
        else:
            total_page = total_size // page_size + 1

        return {
            "current_page_number": int(current_page_number),  # 当前页码
            "page_size": page_size,
            "total_page": total_page,
            "total_size": total_size
        }


def return_json(data_info=None, message=None, headers=None, status_code=200, button_status=True):
    """返回数据类型,统一返回数据的结构"""

    if data_info is None:
        assert message, "如果返回数据为空,messgae信息就是必填项"

    data = {
        "data_info": data_info,
        "message": message,
        "status_code": status_code,
        "button_status": button_status
    }
    return response.HTTPResponse(
        response.json_dumps(data),
        headers=headers,
        status=200,
        content_type="application/json;charset=utf-8"
    )

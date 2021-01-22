import re


def judge_mobile_phone(phone_number):
    """
    正则校验手机号
    :param phone_number: 手机号
    """
    # 正则校验手机号
    pattern = re.compile(r"^1[35678]\d{9}$")
    ret = pattern.match(phone_number)
    if ret is None:
        return False
    return True


def judge_username(username):
    """
    正则校验用户名
    用户名必须包含至少一个大写字母、一个小写字母和一个数字,并且必须以大写字母开头,小写字母次之,数字再次之,长度至少为8位
    :param username: 用户名
    """
    pattern = re.compile(r"^([A-Z]+)(?=.*[a-z])(?=.*\d)[a-zA-Z\d]{7,}$")
    ret = pattern.match(username)
    if ret is None:
        return False
    return True

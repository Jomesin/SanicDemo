from hashlib import md5, sha256


def md5_func(value_str: str, salt: str):
    """
    md5加密方法
    :param value_str: 需要加密的字符串
    :param salt: 盐值
    :return: md5加密后的密文
    """
    obj = md5(bytes(salt, encoding="utf-8"))
    obj.update(value_str.encode("utf-8"))
    return obj.hexdigest()


def sha256_func(value_str: str, salt: str):
    """
    sha256加密方法
    :param value_str: 需要加密的字符串
    :param salt: 盐值
    :return: sha256加密后的密文
    """
    obj = sha256(bytes(salt, encoding="utf-8"))
    obj.update(value_str.encode("utf-8"))
    return obj.hexdigest()

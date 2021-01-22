from sqlalchemy import Column, String, Enum, DateTime, Date, Boolean, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from base64 import b64encode as base64_b64encode
from app.utils.encrypt import md5_func, sha256_func
from app import SingletonApp
from json import dumps as json_dumps
from datetime import datetime
from copy import deepcopy
from hashlib import md5
from time import mktime


UserClass = declarative_base(bind=SingletonApp.app.engine)  # 创建对象的基类,在使用ORM创建数据表时必须继承该类


class UsersModel(UserClass):
    """用户模型"""

    __tablename__ = "users_user"

    id = Column(BigInteger, primary_key=True, autoincrement=True, unique=True, index=True, comment="用户ID(自增长)")
    username = Column(String(20), nullable=False, unique=True, index=True, comment="用户名")
    password = Column(String(150), nullable=False, comment="密码")
    mobile_phone = Column(String(11), nullable=False, index=True, unique=True, comment="手机号")
    sex = Column(Enum("其他", "男", "女"), nullable=False, default="其他", comment="性别")
    email = Column(String(50), nullable=False, index=True, unique=True, comment="邮箱")
    name = Column(String(20), nullable=True, comment="姓名")
    access_token = Column(String(200), nullable=False, comment="用户登录Token")
    last_login_ip = Column(String(20), nullable=False, comment="最后一次登录的ip地址")
    last_login_datetime = Column(DateTime, nullable=False, comment="最后一次登录时间")
    register_date = Column(Date, nullable=False, comment="注册日期")
    status = Column(Boolean, nullable=False, default=True, comment="用户状态(True正常/False异常)")

    def __repr__(self):
        return "<User('%s')>" % self.username

    __str__ = __repr__

    @staticmethod
    def md5_encryption(pwd, salt_list, times=1):
        """
        md5加密算法,按配置文件配置的盐值和加密次数进行加密
        :param pwd: 原始密码
        :param salt_list: 盐值数组
        :param times: 加密次数
        :return: 密文
        """

        obj = md5(bytes(salt_list[times - 1], encoding="UTF-8"))
        obj.update(pwd.encode("UTF-8"))  # 加盐
        secret = obj.hexdigest()  # 加盐后的密文
        if times < SingletonApp.app.config["TRY_TIMES"]:  # 递归出口
            times += 1
            return UsersModel.md5_encryption(secret, salt_list, times)
        return secret

    @staticmethod
    def get_token(payload: dict, salt: str, datetime_now: datetime, active_second=43200):
        """
        自定义加密处JWT Token
        1: header字典去除引号和冒号之间空格转换为json字符串
        2: header字符串转为base64字符串
        3: 深拷贝payload字典,并且添加失效时间键值对
        4: payload字典去除引号和冒号之间空格转换为json字符串
        5: payload字符串转为base64字符串
        6: md5加盐加密后的header.md5加盐加密后的payload.base64编码sha256后的字节对象(header和payload组成)
        :param payload: payload字典
        {
            "user_id": 1234,
            "admin": True
        }
        :param salt: 盐值
        :param datetime_now: 用户最后一次登录时间
        :param active_second: 失效时间(单位:秒)
        :return: JWT Token字符串对象
        """
        header = {"alg": "SHA256", "type": "JWT"}
        header_json = json_dumps(header, sort_keys=True, separators=(",", ":"))
        jwt_header = base64_b64encode(header_json.encode("UTF-8"))  # JWT header部分

        payload = deepcopy(payload)  # 深拷贝JWT payload部分
        payload["active_time"] = mktime(datetime_now.timetuple()) + active_second  # 从服务器获取时间往后推延12小时,设置用户Token有效期12小时
        payload_json = json_dumps(payload, sort_keys=True, separators=(",", ":"))
        jwt_payload = base64_b64encode(payload_json.encode("UTF-8"))  # JWT header部分

        jwt_header = md5_func(str(jwt_header), salt)  # 将header部分进行加密MD5加密
        jwt_payload = md5_func(str(jwt_payload), salt)  # 将payload部分进行加密MD5加密
        # 第三部分使用header部分的alg加密协议进行加密,然后进行base64编码
        jwt_signature = base64_b64encode(sha256_func(jwt_header + "." + jwt_payload, salt).encode("UTF-8"))

        # 三部分转字节后拼接在一起
        return (bytes(jwt_header, encoding="UTF-8") + b"." + bytes(jwt_payload,
                                                                   encoding="UTF-8") + b"." + jwt_signature).decode(
            "UTF-8")

    @staticmethod
    def verification_password(source_password: str, password: str, salt_list):
        """
        校验密码
        :param source_password: 原始密码(前端传入的密码,未加密过得)
        :param password: 用户存储在数据表的密码
        :param salt_list: 盐值数组
        :param times: 加密次数
        :return: Boolean (True密码正确/False密码错误)
        """
        # 将前端传入的密码进行加密
        new_password = UsersModel.md5_encryption(source_password, salt_list)
        # 判断加密后的密码和数据库存储的密码进行比对
        if new_password == password:
            return True
        else:
            return False


if __name__ == '__main__':
    UserClass.metadata.create_all(SingletonApp.app.engine)

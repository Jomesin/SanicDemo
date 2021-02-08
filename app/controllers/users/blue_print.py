from users.models import UsersModel
from users.utils import judge_mobile_phone, judge_username
from users.status_code import StatusCode
from sanic import Blueprint
from app.utils import response, decorator, messages
from datetime import datetime, date
from sqlalchemy.orm import sessionmaker
import re
import random
import string

users = Blueprint("users", url_prefix="/users")


@users.get("/get_phone_code")
@decorator.judge_request_json({
    "phone_number": ("手机号不能为空!", StatusCode.PHONE_NUMBER_EMPTY)
}, response.return_json)
async def user_phone_code(request):
    """
    获取手机号验证码
    /users/get_phone_code?phone_number=18772993902
    1:获取url传输的手机号
    2:手机号非空判断,如果为空返回响应
    3:利用正则校验手机号,如果错误返回响应
    4:随机生成6位的手机验证码
    5:将手机验证码存入0号redis数据库
    6:返回响应
    """
    # 获取请求参数
    query_params = request.args
    phone_number = query_params.get("phone_number", None)

    # 正则校验手机号
    ret = re.match(r"^1[35678]\d{9}$", phone_number)
    if ret is None:
        return response.return_json(message="请检查一下手机号是否正确", status_code=StatusCode.PHONE_NUMBER_ERROR)

    # 随机生成6位的手机验证码
    phone_code = "".join(random.sample([x for x in string.digits], 6))

    # 存入redis数据库
    with await request.app.redis as r_conn:
        await r_conn.select(0)  # 选择手机验证码数据库
        await r_conn.set("phone_number_" + phone_number, phone_code, expire=60 * 15)  # 设置有效期为15分钟

    return response.return_json(message=messages.CodeDict.SUCCESS[1],
                                status_code=messages.CodeDict.SUCCESS[0])


@users.post("/register")
@decorator.judge_request_json({
    "phone_number": ("手机号不能为空!", StatusCode.PHONE_NUMBER_EMPTY),
    "phone_code": ("手机验证码为空!", StatusCode.PHONE_CODE_EMPTY),
    "username": ("用户名为空!", StatusCode.USERNAME_EMPTY),
    "password": ("密码为空!", StatusCode.PASSWORD_EMPTY),
    "email": ("邮箱地址为空!", StatusCode.EMAIL_EMPTY)
}, response.return_json)
async def user_register(request):
    """
    用户注册
    请求方法: POST
    请求数据类型: JSON
    返回响应数据类型: JSON
    {
        "phone_number": "18772993902",
        "phone_code": "308462",
        "username": "Js747142549",
        "password": "123456",
        "name": "JISO",
        "email": "747142549@qq.com"
    }
    1:获取所有请求数据
    2:请求数据非空判断
    3:正则校验部分数据
    4:查询redis判断验证码
    5:查询mysql判断账号和手机号
    6:加密密码,生成JWT Token
    7:开启事务存储用户数据
    """
    # 获取请求体数据
    data = request.json
    mobile_phone = data["phone_number"]  # 手机号
    username = data["username"]  # 用户名
    email = data["email"]  # 邮箱
    password = data["password"]  # 密码

    # 正则判断手机号输入有误
    judge_status = judge_mobile_phone(phone_number=mobile_phone)
    if judge_status is False:
        return response.return_json(message="手机号输入有误!",
                                    status_code=StatusCode.PHONE_NUMBER_ERROR)

    # 正则判断用户名输入有误
    judge_status = judge_username(username=username)
    if judge_status is False:
        return response.return_json(message="用户名输入有误!",
                                    status_code=StatusCode.USERNAME_ERROR)

    # 判断手机号是否存在验证码
    with await request.app.redis as r_conn:
        await r_conn.select(0)
        phone_code = await r_conn.get("phone_number_" + mobile_phone)
        if phone_code:
            phone_code = phone_code.decode("utf-8")
            # 判断手机验证码和用户输入是否一样
            if phone_code != data["phone_code"]:
                return response.return_json(message="手机验证码错误!",
                                            status_code=StatusCode.PHONE_CODE_ERROR)
        else:
            return response.return_json(message="手机验证码失效或者为空,请重新请求验证码",
                                        status_code=StatusCode.PHONE_CODE_EMPTY)

    # 创建Session类
    session = sessionmaker(bind=request.app.engine)
    # 实例session对象
    db_session = session()
    # 查询手机是否存在
    user_queryset = db_session.query(UsersModel.mobile_phone).filter(UsersModel.mobile_phone == mobile_phone).first()
    if user_queryset:
        return response.return_json(message="手机号被注册!", status_code=StatusCode.PHONE_NUMBER_EXISTENCE)

    # 查询用户名是否存在
    user_queryset = db_session.query(UsersModel.username).filter(UsersModel.username == username).first()
    if user_queryset:
        return response.return_json(message="用户名被注册!", status_code=StatusCode.USERNAME_EXISTENCE)

    # 注册用户,存储用户数据信息
    # 获取现在时间
    last_login_datetime = datetime.now()
    # 加密密码
    secret_password = UsersModel.md5_encryption(password, request.app.config["SALT_ARRAY"])
    # 生成JWT Token
    jwt_token = UsersModel.get_token({"username": username, "admin": True},
                                     request.app.config["SALT_ARRAY"][-1],
                                     datetime_now=last_login_datetime)
    try:
        user = UsersModel(
            username=username,
            password=secret_password,
            mobile_phone=mobile_phone,
            sex=data.get("sex", "其他"),
            email=email,
            name=data.get("name", "name_" + username),
            access_token=jwt_token,
            last_login_ip=request.ip,
            last_login_datetime=last_login_datetime,
            register_date=date.today()
        )
        db_session.add(user)
        db_session.commit()  # 提交
        return response.return_json(message=messages.CodeDict.SUCCESS[1],
                                    headers={
                                        "Authorization": jwt_token  # JWT Token存储
                                    }, status_code=messages.CodeDict.SUCCESS[0])
    except Exception as DatabaseError:
        db_session.rollback()
        return response.return_json(message=messages.CodeDict.FAIL[1],
                                    status_code=messages.CodeDict.FAIL[0])


@users.post("/login")
@decorator.judge_request_json({
    "username": ("用户名为空!", StatusCode.USERNAME_EMPTY),
    "password": ("密码为空!", StatusCode.PASSWORD_EMPTY)
}, response.return_json)
async def user_login(request):
    """
    用户登录
    {
        "username": "Js747142549",
        "password": ""
    }

    """
    data = request.json
    username = data["username"]
    source_password = data["password"]

    # 正则判断用户名输入有误
    judge_status = judge_username(username=username)
    if judge_status is False:
        return response.return_json(message="用户名输入有误!",
                                    status_code=StatusCode.USERNAME_ERROR)

    # 查询数据库中用户的密码
    # 创建Session类
    session = sessionmaker(bind=request.app.engine)
    # 实例session对象
    db_session = session()
    # 查询该用户的密码
    user_object = db_session.query(UsersModel).filter(UsersModel.username == username).first()
    if user_object is None or not user_object:
        return response.return_json(message="登录失败,账户或者密码错误", status_code=StatusCode.USERNAME_PASSWORD_ERROR)

    # 校验密码
    verification_status = UsersModel.verification_password(source_password, user_object.password,
                                                           request.app.config["SALT_ARRAY"])
    # 校验通过
    if verification_status:
        # 获取现在时间
        last_login_datetime = datetime.now()
        # 获取JWT Token
        jwt_token = UsersModel.get_token({"username": username, "admin": True},
                                         request.app.config["SALT_ARRAY"][-1],
                                         datetime_now=last_login_datetime)
        # 更新用户信息数据
        try:
            user_object.access_token = jwt_token
            user_object.last_login_ip = request.ip
            user_object.last_login_datetime = last_login_datetime
            db_session.commit()  # 提交
            return response.return_json(data_info=response.DataInfo(list_data=user_object.get_user()), message=messages.CodeDict.SUCCESS[1], status_code=messages.CodeDict.SUCCESS[0])
        except Exception as error:
            print(error)
            db_session.rollback()  # 回滚
            return response.return_json(message=messages.CodeDict.FAIL[1],
                                        status_code=messages.CodeDict.FAIL[0])
    else:
        return response.return_json(message="登录失败,账户或者密码错误", status_code=StatusCode.USERNAME_PASSWORD_ERROR)

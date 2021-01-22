class StatusCode(object):

    PHONE_NUMBER_EMPTY = 101  # 手机号为空
    PHONE_NUMBER_ERROR = 102  # 手机号错误
    USERNAME_EMPTY = 103  # 用户名为空
    USERNAME_ERROR = 104  # 用户名错误
    EMAIL_EMPTY = 105  # 邮箱地址为空
    EMAIL_ERROR = 106  # 邮箱地址错误
    PHONE_CODE_EMPTY = 107  # 手机验证码为空或者不存在
    PHONE_CODE_ERROR = 108  # 手机验证码错误
    PASSWORD_EMPTY = 109  # 密码为空
    PASSWORD_ERROR = 110  # 密码错误
    NAME_ERROR = 111  # 昵称错误
    PHONE_NUMBER_EXISTENCE = 112  # 手机号被注册
    USERNAME_EXISTENCE = 113  # 用户名被注册
    USERNAME_PASSWORD_ERROR = 114  # 账号或者密码错误

# -*- coding: utf-8 -*-
"""
Module usage:
初始化app及各种配置，拓展，中间件，蓝图的地方
"""
from app.middleware import MIDDLEWARE
from config import get_config
from sanic_cors import CORS
from app import controllers
from sanic import Sanic
from sqlalchemy import create_engine
from sanic_redis import SanicRedis
from importlib import import_module
import logging.config
import os
import pymysql

pymysql.install_as_MySQLdb()

__all__ = ["SingletonApp"]


class SingletonApp(object):
    """使用单例模式进行初始化Sanic项目"""

    _instance = None
    app = Sanic(__name__)

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SingletonApp, cls).__new__(cls)
        return cls._instance

    def create_app(self, env=None):
        """
        Create an app with config file
        生成app，并配置各种插件等等
        :return: sanic App
        """
        config = get_config(env)

        # 配置日志
        logging.config.dictConfig(config.BASE_LOGGING)

        # 加载sanic的配置内容
        SingletonApp.app.config.from_object(config)

        # 配置所有的sanic扩展
        self.configure_extensions()

        # 配置中间件
        self.configure_middleware()

        # 创建数据库连接引擎
        self.configure_database()

        # 创建缓存数据库连接
        self.configure_redis()

        # 配置蓝图
        self.configure_blueprints()

    @classmethod
    def configure_extensions(cls):
        """初始化所有第三方插件"""
        # cors
        if cls.app.config.get("ENABLE_CORS"):
            CORS(cls.app)

    @classmethod
    def configure_blueprints(cls):
        """
        Register BluePrints for sanic
        通过文件夹灵活导入蓝图，只要在 app.controllers.__init__.py 文件中添加新的蓝图名即可
        :return:
        """
        controller_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'controllers')
        for module_name in controllers.__all__:
            module_path = os.path.join(controller_dir, module_name)

            assert os.path.isdir(module_path) and not module_name.startswith('__'), \
                f'{module_name} 不是有效的文件夹, 无法导入模块'

            # 导入蓝图文件
            module = import_module(f"app.controllers.{module_name}.blue_print")
            cls.app.blueprint(getattr(module, module_name))

    @classmethod
    def configure_middleware(cls):
        """
        Register middleware for sanic
        通过app的 register_middleware() 注册中间件，此次分别在request和reponse时进行注册
        新增中间件，只需在 app.middleware.__init__.py 文件中添加中间件类名即可
        """
        for middle in MIDDLEWARE:
            cls.app.register_middleware(middle.before_request, attach_to="request")
            cls.app.register_middleware(middle.after_request, attach_to="response")

    @classmethod
    def configure_database(cls):
        """配置数据库连接"""
        database_dict = cls.app.config["DATABASE"]

        cls.app.engine = create_engine(
            "{DATABASE_TYPE}://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}?charset={CHARSET}".format(
                DATABASE_TYPE=database_dict["DATABASE_TYPE"],
                USER=database_dict["USER"],
                PASSWORD=database_dict["PASSWORD"],
                HOST=database_dict["HOST"],
                PORT=database_dict["PORT"],
                DB=database_dict["DB"],
                CHARSET=database_dict["CHARSET"]),
            encoding="utf8",
            echo=True,  # 设置为True会将ORM语句转化为sql,生产环境关闭
            echo_pool=True,
            pool_size=20,  # 连接池大小20
            pool_recycle=60 * 30,
            pool_timeout=20,  # 池中没有线程最多等待的时间,否则报错
            pool_pre_ping=True  # 表示每次连接从池中检查,如果有错误,监测为断开状态,连接将被立即断开
        )

    @classmethod
    def configure_redis(cls):
        """配置redis数据库"""
        cls.app.config.update({
            "redis": cls.app.config["REDIS"]
        })
        SanicRedis(cls.app, config_name="redis")

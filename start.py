# -*- coding: utf-8 -*-
from app import SingletonApp
from app.core import logger

env = "LOCAL"
host = "10.70.6.188"
port = 8001

app_object = SingletonApp()
app_object.create_app(env)
workers = app_object.app.config.get('WORKERS')
app_object.debug = app_object.app.config.get('DEBUG')

if __name__ == '__main__':
    logger.info("""
       _____             _         _____ _             _     _ 
      / ____|           (_)       / ____| |           | |   | |
     | (___   __ _ _ __  _  ___  | (___ | |_ __ _ _ __| |_  | |
      \___ \ / _` | '_ \| |/ __|  \___ \| __/ _` | '__| __| | |
      ____) | (_| | | | | | (__   ____) | || (_| | |  | |_  |_|
     |_____/ \__,_|_| |_|_|\___| |_____/ \__\__,_|_|   \__| (_)
     地址: {HOST}
     端口: {PORT}
     运行 {WORKERS} 个工作者
     运行在 {ENV} 环境
    """.format(HOST=host, PORT=port, WORKERS=workers, ENV=env))
    app_object.app.run(host=host, port=port, workers=workers, auto_reload=False)

#!/usr/bin/env python3
# coding=UTF-8
from flask import Flask
from app.models.base import db

# 蓝图注册函数
def register_api_blueprint(app):
    from app.api import api
    app.register_blueprint(api, url_prefix='/api')
    from app.web import web
    app.register_blueprint(web, url_prefix='/web')


def create_app(config=None):
    app = Flask(__name__)

    #: 加载配置
    app.config.from_object('app.settings')

    # 注册SQLAlchemy
    db.init_app(app)

    # 接口蓝图注册
    register_api_blueprint(app)

    if config is not None:
        if isinstance(config, dict):
            app.config.update(config)
        elif config.endswith('.py'):
            app.config.from_pyfile(config)
    return app

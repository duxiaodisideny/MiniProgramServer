#!/usr/bin/env python3
# coding=UTF-8
'''
@Date: 2020-04-08 17:25:07
@LastEditTime: 2020-04-08 19:15:57
@Description: file content
'''
from app import create_app
from app.models import db
from flask_cors import CORS

# 初始化app
app = create_app()
# 跨域支持
CORS(app, supports_credentials=True)
# 初始化数据库
with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)

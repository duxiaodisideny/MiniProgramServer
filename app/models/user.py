#!/usr/bin/env python3
# coding=UTF-8
from sqlalchemy import Column, String, Integer
from app.models.base import db, Base  # noqa
from flask import g
from datetime import datetime


class User(Base):
    __tablename__ = 'user'

    userName = Column("username", String(64), nullable=False)
    userOpenId = Column("user_open_id", String(128),
                        unique=True, nullable=False)
    phoneNum = Column("phone_num", String(64), unique=True, nullable=False)
    # 地址
    location = Column(String(256))
    # 公司
    company = Column(String(512))
    roles = Column("roles", Integer, default=1)
    token = Column(String(512), default=None)

    # 联合索引
    __table_args__ = (
        db.Index('user_id_open_id_token_index', "id", 'user_open_id', 'token'),
    )

    # 查询用户信息主要用于登录的时候拉取用户信息
    def query_user(self, params):
        if not isinstance(params, dict) or not params:
            return None
        user = User.query.filter_by(**params).first()
        if user:
            return user
        return None

    def check_register_fields(self, form):
        for key, value in form.items():
            # 如果有空值返回false
            if hasattr(self, key):
                if not value:
                    return g.sc.params_missing

                # 其他字段必须是字符串
                elif not isinstance(value, str):
                    return g.sc.params_type_error
        return False

    def update_token(self, tk):
        self.token = tk
        self.updateDate = int(datetime.now().timestamp())
        db.session.commit()

    @property
    def required_fields(self):
        return ['userName', 'phoneNum', 'location', 'company']

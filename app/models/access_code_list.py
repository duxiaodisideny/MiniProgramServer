#!/usr/bin/env python3
# coding=UTF-8
from sqlalchemy import Column, String
from app.models.base import db, Base  # noqa


class AccessCodeList(Base):
    __tablename__ = 'access_code_list'

    accessCode = Column('access_code', String(32))
    userOpenId = Column('user_open_id', String(128), index=True)

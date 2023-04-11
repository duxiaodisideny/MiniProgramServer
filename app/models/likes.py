#!/usr/bin/env python3
# coding=UTF-8

from sqlalchemy import Column, SmallInteger, Integer
from app.models.base import db, Base


class Likes(Base):
    __tablename__ = 'likes'

    # 点赞对象id文档或者视频的id
    targetId = Column("target_id", Integer, nullable=False)
    # 点赞人id
    userId = Column("user_id", Integer, nullable=False)
    # 点赞的类型，1文档 2视频
    kind = Column("kind", SmallInteger, nullable=False)

    # 联合索引
    __table_args__ = (
        db.Index('target_id_user_id_kind', "target_id", 'user_id', 'kind'),
    )

    @property
    def required_fields(self):
        return ['targetId']

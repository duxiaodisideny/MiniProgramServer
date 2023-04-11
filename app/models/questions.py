#!/usr/bin/env python3
# coding=UTF-8
from sqlalchemy import Column, String, Integer, Text
from app.models.base import db, Base
from app.models.video import Video


class Questions(Base):
    __tablename__ = 'questions'

    # nullable能否空，unique是否唯一
    videoId = Column("video_id", Integer, nullable=False)
    questionTitle = Column(
        "question_title", String(256), nullable=False, unique=True)
    userId = Column("user_id", Integer, nullable=False)
    questionStatus = Column("question_status", db.Boolean, default=False)
    questionAnswer = Column("question_answer", Text, default=None)

    # 联合索引
    __table_args__ = (db.Index('target_id_user_id_kind', "video_id", 'user_id',
                               'question_status'), )

    @property
    def required_fields(self):
        return ['videoId', "questionTitle", "userId"]

    @property
    def video(self):
        res = Video.query.order_by(
            Video.id).filter(Video.id == self.videoId).first()
        return res.to_json() if res else {}

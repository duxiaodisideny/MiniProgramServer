#!/usr/bin/env python3
# coding=UTF-8
from sqlalchemy import Column, String
from sqlalchemy import Integer
from app.models.base import Base


class Video(Base):
    __tablename__ = 'video'
    videoName = Column('video_name', String(256), nullable=False)
    videoCoverSrc = Column('video_coverSrc', String(256), nullable=False)
    videoSrc = Column("video_src", String(256), nullable=False)
    videoGoodCount = Column("video_good_count", Integer, default=0)
    videoType = Column("video_type", String(256), default=None)

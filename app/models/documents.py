#!/usr/bin/env python3
# coding=UTF-8
from sqlalchemy import Column, Integer, Text, String
from app.models.base import db, Base


class Documents(Base):
    __tablename__ = 'documents'
    docName = Column("doc_name", String(512), nullable=False)
    docCoverSrc = Column("doc_cover_src", String(512), nullable=False)
    docSrc = Column('doc_src', String(512), nullable=False)
    content = Column(Text)
    userId = Column("user_id", Integer, nullable=False)
    docGoodCount = Column("doc_good_count", Integer, default=0)

    # 联合索引
    __table_args__ = (
        db.Index('doc_id_user_id_doc_name_index', "id", 'doc_name', 'user_id'),
    )

    @property
    def required_fields(self):
        return ['docName', "docCoverSrc", "docSrc"]

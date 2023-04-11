#!/usr/bin/env python3
# coding=UTF-8
from sqlalchemy import Column, String, SmallInteger
from app.models.base import db, Base  # noqa


class SMSHistory(Base):
    __tablename__ = 'sms_history'

    phoneNumber = Column('phone_number', String(64),
                         nullable=False)
    text = Column(String(128), nullable=False)
    template_code = Column('template_code', String(
        128), nullable=False, default="SMS_192365145")
    checked = Column(SmallInteger, nullable=False, default=0)

    __table_args__ = (
        db.Index('phone_number_text_checked_index',
                 "phone_number", 'text', 'checked'),
    )

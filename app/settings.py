#!/usr/bin/env python3
# coding=UTF-8
import os

SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://'  # 数据库配置
WX_LOGIN_CHECK_URL = 'https://api.weixin.qq.com/sns/jscode2session'
ACCESS_KEY_ID = ""  # 小程序ID
ACCESS_SECRET = ""  # 小程序Secret
CDN = "default"
SIGN_NAME = ""  # 签名
# 发送短信每次间隔60秒
SMS_INTERVAL = 60
# 验证码有效期单位秒
SMS_CODE_EXPIRED = 300
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_AUDIO_PATH = os.path.join(BASE_DIR, "static", "UpdateAudio")
MERGE_AUDIO_PATH = os.path.join(BASE_DIR, "static", "MergeAudio")
APPKEY = ''  # 阿里云短信AppKey
TOKEN = ''  # 阿里云短信Token
SQLALCHEMY_POOL_SIZE = 1024
SQLALCHEMY_POOL_TIMEOUT = 90
SQLALCHEMY_POOL_RECYCLE = 3
SQLALCHEMY_MAX_OVERFLOW = 1024

#!/usr/bin/env python3
# coding=UTF-8
import json
import re
import os
import random
import requests
from datetime import datetime
from faker import Faker
from flask import current_app, g, Response, jsonify, request
from sqlalchemy import func

from . import api
from app.models.verified_company import VerifiedCompany
from app.models.literacy_game_material import LiteracyGameMaterial
from app.models.wordseries_game_material import WordSeriesGameMaterial
from app.models.user import User
from app.models.video import Video
from app.models.documents import Documents
from app.models.questions import Questions
from app.models.likes import Likes
from app.models.access_code_list import AccessCodeList
from app.models.sms_history import SMSHistory
from app.models import db
from app.libs.status_code import StatusCode
from app.libs.decorator import login_required, parse_json
from app.libs.jwt_tool import JWT
from app.libs.send_sms import SendSms
from app.libs.speech_recognizer import SpeechHandle


@api.before_app_request
def handle_result():
    # 每次请求先全局实例化
    g.sc = StatusCode()
    g.sms_sender = SendSms()


def get_open_id(form):
    # 这4个请求参数是必填的
    fileds = ["js_code"]
    # 校验是不是每个参数都有并且不是空
    # 从请求中取需要的字段，防止有不需要的字段在里面
    params = {key: value for key, value in form.items() if key in fileds}
    try:
        # 请求微信
        url = f'{current_app.config.get("WX_LOGIN_CHECK_URL")}?{"appid=wxa399b622820e38d0"}&{"secret=e29cd0afabe71f03e7e91b85868b852d"}&{params.get("js_code")}&{"grant_type=authorization_code"}'
        res = requests.get(url, params=params)

        res = res.json()
        # 如果返回的code码不是0，就是错误，直接返回微信返回的错误信息
        if res.get("errcode"):
            return g.sc.fail(msg=res.get("errmsg"))
    except Exception as e:
        print(e)
        return g.sc.system_inner_error
    return g.sc.success(res.get("openid"))


@api.route('/get_openid', methods=['GET', 'POST'])
@parse_json
def get_openid(data):
    res = get_open_id(data)
    if res.get('code') != 0:
        return jsonify(res)
    open_id = res.get('data')

    return jsonify(open_id)


# ------------------------------------ 注册 ------------------------------------ #
@api.route('/register', methods=['GET', 'POST'])
@parse_json  # 这个装饰器是判断参数是否有和解析参数json
def register(data):
    messageCode = data.get('messageCode')
    phoneNum = data.get('phoneNum')
    open_id = data.get('openid')
    # 没有验证码
    if not messageCode or not open_id:
        return jsonify(g.sc.params_missing)

    user = User()
    res = user.check_register_fields(data)
    # 有返回的说明是验证必填参数有缺失的
    if res:
        jsonify(res)
    # openid注册过
    has = User.query.filter_by(userOpenId=open_id).first()
    if has:
        return jsonify(g.sc.user_already_registered)
    # 手机号注册过
    has = User.query.filter_by(phoneNum=phoneNum).first()
    if has:
        return jsonify(g.sc.operation_failed('当前手机号注册过！'))
    # 根据手机号和验证码以及验证是没有验证过的就可以找到对应的验证码的记录了
    has_sms = SMSHistory.query.filter_by(
        phoneNumber=phoneNum, text=messageCode, checked=0).first()

    # 没有查询到验证码
    if not has_sms:
        return jsonify(g.sc.operation_failed('验证码错误！'))

    now = int(datetime.now().timestamp())
    # 验证码过期
    if current_app.config.get(
            "SMS_CODE_EXPIRED") < now - has_sms.createDate:
        return jsonify(g.sc.operation_failed('验证码已过期，请重新发送！'))

    # 设置用户所有属性
    form = {key: value for key, value in data.items() if hasattr(user, key)}
    form["userOpenId"] = open_id
    form["id"] = User.query.filter_by(User.id.desc()).first().id + 1
    try:
        user.set_attrs(form)
        # 保存用户
        db.session.add(user)
        # 更新验证码用过
        has_sms.checked = 1
        db.session.commit()

    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify(g.sc.system_inner_error)

    return jsonify(g.sc.success())

# ------------------------------------ 登录 ------------------------------------ #


@api.route('/login', methods=['GET', 'POST'])
@parse_json
def login(data):
    # res = get_open_id(data)
    # if res.get('code') != 0:
    #     return jsonify(res)
    # open_id = res.get('data')
    open_id = data.get('openid')
    jwt = JWT()
    # 创建token并且保存到用户的表里
    token = jwt.gen_token(open_id)
    if not token:
        return jsonify(g.sc.login_error)
    return jsonify(g.sc.success(token))


@api.route('/check_user', methods=['GET', 'POST'])
@parse_json
def check_user(data):
    # res = get_open_id(data)
    # if res.get('code') != 0:
    #     return jsonify(res)
    open_id = data.get('openid')
    user_status = User.query.filter_by(userOpenId=open_id).first()
    if user_status:
        return jsonify(True)
    else:
        return jsonify(False)


@api.route('/check_user_company', methods=['GET', 'POST'])
@parse_json
@login_required
def check_user_company(data):
    companyRealName = data.get('company')
    companStatus = VerifiedCompany.query.filter_by(companyName=companyRealName).first()
    if companStatus:
        return jsonify(True)
    else:
        return jsonify(False)


# ----------------------------------- 注册发送验证码短信 ----------------------------------- #
@api.route('/sendsms', methods=['GET', 'POST'])
@parse_json
def send_sms(data):
    phone_number = data.get('phoneNumber')
    mobile_re = re.compile(
        r'^1([358][0-9]|4[579]|66|7[0135678]|9[89])[0-9]{8}$')
    if not phone_number:
        return jsonify(g.sc.params_missing)

    # 手机号格式错误
    if not mobile_re.match(phone_number):
        return jsonify(g.sc.params_error)

    has_user = User.query.filter_by(phoneNum=phone_number).first()
    # 已经注册过的用户手机号不可以发送短信
    # 由于用户手机号码是唯一的，
    # 所以对于验证码发送历史只是记录验证码发送过的和是否有验证
    # 不需要绑定用户openid,只需要验证这个手机号码有没有注册过
    if has_user:
        return jsonify(g.sc.operation_failed('当前手机号注册过，不能发短信！'))

    has_sms = SMSHistory.query.filter_by(phoneNumber=phone_number).order_by(
        SMSHistory.createDate.desc()).first()
    if has_sms:
        now = int(datetime.now().timestamp())
        # 计算发送间隔
        if current_app.config.get(
                "SMS_INTERVAL") >= now - has_sms.createDate:
            return jsonify(g.sc.operation_too_frequent)
    try:
        # 生成6位数字验证码
        text = random.randrange(100000, 1000000)
        # 发送短信
        resp = g.sms_sender.send(phone_number, text)
        resp = json.loads(resp)
        if(resp.get('Message') != 'OK'):
            return jsonify(False)
        # 入库验证码，
        with db.auto_commit():
            sms = SMSHistory()
            sms.set_attrs(dict(phoneNumber=phone_number, text=f'{text}'))
            sms.id = SMSHistory.query.filter_by(SMSHistory.id.desc()).first().id + 1
            db.session.add(sms)

    except Exception as e:
        print(e)
        return jsonify(False)

    return jsonify(True)


# ------------------------------------ 激活教师权限 ------------------------------------ #
@api.route('/activeTeacher', methods=['GET', 'POST'])
@login_required
@parse_json
def active_teacher(data):
    access_code = data.get('accessCode')
    open_id = data.get('openid')
    if not open_id or not access_code:
        return jsonify(g.sc.params_missing)
    has_active = AccessCodeList.query.filter_by(accessCode=access_code).first()
    # 激活码不存在
    if not has_active:
        return jsonify(g.sc.operation_failed('当前激活码无效！'))

    # 激活码已绑定
    if has_active.userOpenId:
        return jsonify(g.sc.operation_failed('激活码已被绑定！'))
    # 绑定激活码到用户
    has_active.userOpenId = open_id
    # 更新用户角色
    user = db.session.query(User).filter(User.userOpenId == open_id).first()
    user.roles = 1
    db.session.commit()
    user_info = db.session.query(User).filter(User.userOpenId == open_id).first()
    status = user_info.roles
    if status == 1:
        return jsonify(g.sc.success())
    else:
        return jsonify("激活失败！")


# ---------------------------------- 拉取视频列表 ---------------------------------- #
@api.route('/getVideoList', methods=['GET', 'POST'])
@login_required
@parse_json
def get_video_list(data):
    video_type = data.get('videoType')
    if not video_type:
        return jsonify(g.sc.params_missing)
    video = Video()
    video_list = video.query.filter_by(videoType=video_type).all()
    return jsonify(g.sc.success([v.to_json() for v in video_list]))


# ----------------------------------- 点赞视频 ----------------------------------- #
@api.route('/videoZan', methods=['GET', 'POST'])
@login_required
@parse_json
def video_zan(data):
    liker = Likes()
    if liker.check_required_fields(data):
        return jsonify(g.sc.params_missing)
    like = Likes.query.filter_by(targetId=data.get(
        'targetId'), userId=g.user.id).first()
    # 有点赞过就直接返回， 没有点赞过就点赞插入
    if like:
        return jsonify(g.sc.action_fail)
    # 1是文档2是视频
    data["kind"] = 2
    data["userId"] = g.user.id
    Likes().add_object(Likes, data)
    taret_video = Video.query.filter_by(id=data.get('targetId')).first()
    taret_video.videoGoodCount = taret_video.videoGoodCount + 1
    db.session.commit()
    return jsonify(g.sc.success())

# ----------------------------------- 点赞文档 ----------------------------------- #
@api.route('/docZan', methods=['GET', 'POST'])
@login_required
@parse_json
def doc_zan(data):
    liker = Likes()
    if liker.check_required_fields(data):
        return jsonify(g.sc.params_missing)
    like = Likes.query.filter_by(targetId=data.get(
        'targetId'), userId=g.user.id).first()
    # 有点赞过就直接返回， 没有点赞过就点赞插入
    if like:
        return jsonify(g.sc.action_fail)
    # 1是文档2是视频
    data["kind"] = 1
    data["userId"] = g.user.id
    Likes().add_object(Likes, data)
    return jsonify(g.sc.success())

# ----------------------------------- 创建问题 ----------------------------------- #
@api.route('/createQuestion', methods=['GET', 'POST'])
@login_required
@parse_json
def create_question(data):
    data["openId"] = g.user.userOpenId
    res = Questions().add_object(Questions, data)
    if not res:
        return jsonify(g.sc.params_missing)

    return jsonify(g.sc.success())


@api.route('/getuserid', methods=['GET', 'POST'])
@login_required
@parse_json
def get_user_id(data):
    open_id = data.get('openid')
    user = User.query.filter_by(userOpenId=open_id).first()
    user_id = user.id
    return jsonify(user_id)


# --------------------------------- 拉取视频下的问题 --------------------------------- #
@api.route('/getVideoQuestion', methods=['GET', 'POST'])
@login_required
@parse_json
def get_video_question(data):
    video_id = data.get('videoId')
    print(g.user.roles)
    # 管理员的
    if g.user.roles == 100:
        currentPage = data.get('currentPage')
        size = data.get('pageSize')
        paginater = Questions.query.order_by(
            Questions.createDate).filter().paginate(
                page=currentPage, per_page=size)
        res = paginater.items
        data = [q.obj2json(q) for q in res if q]
    else:
        if not video_id:
            return jsonify(g.sc.params_missing)
        # 由于需要用户自己的数据在最前面所以先查询与自己的数据排序
        user_question = Questions.query.order_by(
            Questions.createDate).filter_by(
                userId=g.user.id, videoId=video_id).all()
        # 接着查询其他的数据排序
        other_question = Questions.query.order_by(Questions.createDate).filter(
            Questions.userId != g.user.id,
            Questions.videoId == video_id).all()
        # 合并二次查询的数据
        res = user_question + other_question
        data = [q.to_json() for q in res if q]

    result = g.sc.success(
        data=data, total=paginater.total if g.user.roles == 100 else 0)
    return jsonify(result)



# --------------------------------- 拉取所有文档列表 --------------------------------- #
@api.route('/getDocList', methods=['GET', 'POST'])
@login_required
def get_doc_list():
    doc = Documents()
    doc_list = doc.query.all()
    return jsonify(g.sc.success([d.to_json() for d in doc_list]))


# ---------------------------------- 拉取当前用户的所有提问 --------------------------------- #
@api.route('/getUserQuestionList', methods=['GET', 'POST'])
@login_required
def get_user_question_list():
    question = Questions()
    print(g.user.id)
    q_list = question.query.filter_by(userId=g.user.id).all()
    print(q_list)
    return jsonify(g.sc.success([q.to_json() for q in q_list]))


# ---------------------------------- 拉取当前用户信息 ---------------------------------- #
@api.route('/getUserInfo', methods=['GET', 'POST'])
@login_required
def get_user_info():
    return jsonify(g.sc.success(g.user.to_json()))


# --------------------------------- 更新当前用户信息 --------------------------------- #
@api.route('/updateUserInfo', methods=['GET', 'POST'])
@login_required
@parse_json
def update_user_info(data):
    sex = data.get('sex')
    email = data.get('email')
    if sex:
        g.user.sex = sex
    if email:
        g.user.email = email
    db.session.commit()

    return jsonify(g.sc.success())

# ----------------------------------- 回答问题 ----------------------------------- #


@api.route('/answerQuestion', methods=['GET', 'POST'])
@login_required
@parse_json
def answer_question(data):
    q_id = data.get('questionId')
    answer = data.get('questionAnswer')
    if not q_id or not answer:
        return jsonify(g.sc.params_missing)
    question = Questions.query.filter_by(id=q_id).first()
    # 没找到问题
    if not question:
        return jsonify(g.sc.not_found)
    # 解答过
    if question.questionStatus == True or question.questionAnswer:

        return jsonify(g.sc.question_already_answered)
    # 更新回答和状态
    question.questionAnswer = answer
    question.questionStatus = True
    db.session.commit()

    return jsonify(g.sc.success())


# 语音识别
@api.route('/speechRecognize', methods=['POST'])
def speech_recognize():
    f = request.files['file']
    open_id = request.form.get('open_id')
    mp3_path = os.path.join(current_app.config.get(
        'UPLOAD_AUDIO_PATH'), f"{open_id}.mp3")
    wav_path = os.path.join(current_app.config.get(
        'UPLOAD_AUDIO_PATH'), f"{open_id}.wav")
    f.save(mp3_path)
    print(request.files, open_id, mp3_path, wav_path)
    # access_key_id = 'LTAI4G15iUWMY7yHP4wwGwCk'
    # access_key_secret = 'eHUc485bRnoKN7j5fxbtc9yGiVKvO8'
    s = SpeechHandle(current_app.config.get('APPKEY'),
                     access_key_id=current_app.config.get('ACCESS_KEY_ID'),
                     access_key_secret=current_app.config.get('ACCESS_SECRET'))
    res = s.run_recognizer(mp3_path, wav_path)

    return jsonify(res)


# 语音合成
@api.route('/speechSynthesize', methods=['POST'])
@login_required
@parse_json
def speech_synthesize(data):
    print(data)
    filename = f"{data.get('open_id')}.mp3"
    mp3_path = os.path.join(current_app.config.get(
        'MERGE_AUDIO_PATH'), filename)
    s = SpeechHandle(current_app.config.get('APPKEY'),
                     access_key_id=current_app.config.get('ACCESS_KEY_ID'),
                     access_key_secret=current_app.config.get('ACCESS_SECRET'))
    res = s.run_synthesizer(data.get('text'), mp3_path, filename)
    return jsonify(res)


@api.route('/getLiteracyGame', methods=['GET', 'POST'])
@login_required
@parse_json
def get_literacy_game_material(data):
    content_type = data.get('contentType')
    if not content_type:
        return jsonify(g.sc.params_missing)
    game_content = LiteracyGameMaterial.query.filter_by(contentType=content_type).order_by(func.random()).limit(6).all()
    if not game_content:
        return jsonify(g.sc.not_found)
    return jsonify(g.sc.success([v.to_json() for v in game_content]))


@api.route('/getWordSeriesGame', methods=['GET', 'POST'])
@login_required
@parse_json
def get_wordseries_game_material(data):
    content_type = data.get('contentType')
    if not content_type:
        return jsonify(g.sc.params_missing)
    game_content = WordSeriesGameMaterial.query.filter_by(contentType=content_type).order_by(func.random()).limit(1).all()
    if not game_content:
        return jsonify(g.sc.not_found)
    return jsonify(g.sc.success([v.to_json() for v in game_content]))


# ---------------------------------- 生成随机模拟数据入库 ---------------------------------- #
@api.route('/mockData', methods=['GET', 'POST'])
def mock_data():
    f = Faker(locale="zh_CN")
    count = 1000
    for _ in range(count):

        #  随机添加视频数据
        video = Video()
        video.set_attrs(
            dict(
                videoName=f.sentence(),
                videoCoverSrc=f.url(),
                videoSrc=f.url()))
        db.session.add(video)

        # 随机用户数据
        user = User()
        user.set_attrs(
            dict(
                userName=f.name(),
                userOpenId=f.md5(),
                sex=random.choice(["男", "女"]),
                phoneNum=f.phone_number(),
                location=f.address(),
                company=f.company(),
                email=f.email(),
            ))
        db.session.add(user)

        # 随机问答数据
        status = random.choice([True, False])
        question = Questions()
        question.set_attrs(
            dict(
                videoId=random.randint(1, count),
                questionTitle=f.sentence(),
                userId=random.randint(1, count),
                questionStatus=status,
                questionAnswer=f.text() if status else None,
            ))
        db.session.add(question)

        # 随机文档数据
        doc = Documents()
        doc.set_attrs(
            dict(
                userId=random.randint(1, count),
                docName=f.sentence(),
                docCoverSrc=f.url(),
                docSrc=f.url(),
                content=f.text(),
            ))
        db.session.add(doc)
    db.session.commit()

    for _ in range(count):
        # 随机点赞视频
        v_id = random.randint(1, count)
        video_like = Likes()
        video_like.set_attrs(
            dict(
                targetId=v_id,
                userId=random.randint(1, count),
                kind=2,
            ))
        db.session.add(video_like)
        query_video = Video.query.filter_by(id=v_id)
        video = query_video.first()
        video.videoGoodCount += 1

        # 随机点赞文档
        c_id = random.randint(1, count)
        doc_like = Likes()
        doc_like.set_attrs(
            dict(
                targetId=random.randint(1, count),
                userId=c_id,
                kind=1,
            ))
        db.session.add(doc_like)
        query_doc = Documents.query.filter_by(id=c_id)
        doc = query_doc.first()
        doc.docGoodCount += 1

        db.session.commit()

    return jsonify(g.sc.success())

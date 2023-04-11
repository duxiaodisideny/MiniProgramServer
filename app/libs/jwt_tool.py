#!/usr/bin/env python3
# coding=UTF-8

import time
import sys
# g是全局对象，在flask里面的，我们在初始化的时候
from flask import g
from app.models.user import User
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import itsdangerous


class JWT:
    def __init__(self):

        # 用一个值作为密钥 当然你可以用任何的字符串作为密钥 越复杂越安全
        self.secret_key = "548D859ADA8B084E76730CCEFA052EE1"

        # 除去密钥外 再添加一个盐值来提高安全性
        self.salt_str = "eGwt25ga9D0ivfYxAf2e2QiuxS7mNZuW"

        self.expires_in = 3600 * 24 * 7  # 控制token的过期有效市场 默认为3600

    def gen_token(self, openid):
        s = Serializer(
            secret_key=self.secret_key,
            expires_in=self.expires_in,
            salt=self.salt_str,
        )
        # 查询用户
        user = User().query_user(params={"userOpenId": openid})
        # 拿到用户
        if user:
            # 创建token结果是一组加密数据
            token = s.dumps({"user_id": user.id, "open_id": user.userOpenId,
                             "iat": time.time()}).decode("utf-8")

            # 更新用户token
            user.update_token(token)
            return token
        else:
            pass

    def parser_token(self, token):
        # 用token查询用户如果找不到就没有这个用户登录的记录
        user = User().query_user(params={"token": token})
        if not user:
            # 没有token记录
            return g.sc.token_not_found

        # 实例化解析token
        s = Serializer(secret_key=self.secret_key, salt=self.salt_str)
        try:
            # 尝试解析
            # 这里解析是需要核对token和查询的用户是否一致是否过期
            data = s.loads(token)
            # token解析的和用户查询的结果不一致就是非法
            if data.get("user_id") != user.id:
                return g.sc.token_become_invalid

            # 只有这里才是返回成功的,对当前的全局用户信息赋值，
            # 其他的地方就可以直接用，因为每次有请求都会解析token都会走这里
            g.user = user
            return g.sc.success()
        except itsdangerous.SignatureExpired:
            # token过期了就把他删除
            user.update_token(None)
            return g.sc.token_is_expired
        except itsdangerous.BadSignature as e:
            # 如果上面解析的原因进入这里就验证原因
            # 这里不能删除防止是别人伪造的其他人的token
            if e.payload:
                try:
                    s = s.load_payload(e.payload)
                    print(s)
                    # 已泄露非法token
                    return g.sc.token_become_invalid
                except Exception:
                    print(str(sys.exc_info()))
            # 非法token
            return g.sc.token_become_invalid
        except Exception:
            print(str(sys.exc_info()))
            # 以上原因都不是就是解析失败
            return g.sc.token_parsing_failed

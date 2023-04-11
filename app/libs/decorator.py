#!/usr/bin/env python3
# coding=UTF-8

from flask import request, g, jsonify
import sys
from .jwt_tool import JWT
from functools import wraps


# 判断和解析请求的的json
def parse_json(fun):
    @wraps(fun)
    def inner(*arg, **kwargs):
        input_data = request.json
        # 如果请求没有参数返回参数缺失
        if not input_data:
            return jsonify(g.sc.params_missing)
        return fun(input_data, *arg, **kwargs)
    return inner


# 验证用户登录装饰器
def login_required(fun):
    @wraps(fun)
    def inner(*arg, **kwargs):
        try:
            token = request.headers.get("token")
            # 获取token空
            if not token:
                return jsonify(g.sc.token_not_found)
            jwt = JWT()
            sc_result = jwt.parser_token(token)
            # 如果返回的结果code不是0就说明有问题的直接返回
            if sc_result.get("code") != 0:
                return jsonify(sc_result)
        except Exception:
            print(str(sys.exc_info()))
            # 获取登录出错
            return jsonify(g.sc.get_user_info_error)
        return fun(*arg, **kwargs)
    return inner

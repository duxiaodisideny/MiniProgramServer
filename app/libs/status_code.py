#!/usr/bin/env python3
# coding=UTF-8

class StatusCode:
    def __init__(self):
        self.init()

    def init(self):
        self._data = {"msg": "成功", "data": [],
                      "code": 0, "total": 0, "page_count": 0}

    def success(self, data=None, total=0, page_count=0, msg=None):
        self.init()
        self._data["data"] = data or []
        self._data["msg"] = msg or "success"
        self._data["code"] = 0

        return self._data

    def fail(self, data=None, msg=None, code=-1):
        self.init()
        self._data["data"] = data or []
        self._data["msg"] = msg or "failed"
        self._data["code"] = code

        return self._data

    @property
    def data(self):
        return self._data

    @property
    def no_permission(self):
        self.init()
        self._data["code"] = 1001
        self._data["msg"] = '没有权限'

        return self._data

    @property
    def system_inner_error(self):

        self.init()
        self._data["code"] = 1002
        self._data["msg"] = '系统繁忙，请稍候重试'

        return self._data

    @property
    def method_error(self):

        self.init()
        self._data["code"] = 1003
        self._data["msg"] = '请求方法错误'

        return self._data

    @property
    def login_error(self):

        self.init()
        self._data["code"] = 1004
        self._data["msg"] = '登录失败'

        return self._data

    @property
    def token_not_found(self):
        self.init()
        self._data["code"] = 1005
        self._data["msg"] = '没有找到Token'
        return self._data

    @property
    def token_parsing_failed(self):
        self.init()
        self._data["code"] = 1006
        self._data["msg"] = 'Token 解析失败!'
        return self._data

    @property
    def token_become_invalid(self):
        self.init()
        self._data["code"] = 1007
        self._data["msg"] = 'Token非法'
        return self._data

    @property
    def token_is_expired(self):
        self.init()
        self._data["code"] = 1008
        self._data["msg"] = 'Token过期，请重新登录'
        return self._data

    @property
    def params_missing(self):
        self.init()
        self._data["code"] = 1009
        self._data["msg"] = '参数缺失'

        return self._data

    @property
    def get_user_info_error(self):
        self.init()
        self._data["code"] = 1010
        self._data["msg"] = '获取用户信息失败请先登录'

        return self._data

    @property
    def params_error(self):
        self.init()
        self._data["code"] = 1011
        self._data["msg"] = '参数错误'

        return self._data

    @property
    def params_type_error(self):
        self.init()
        self._data["code"] = 1012
        self._data["msg"] = '参数类型不对'

        return self._data

    @property
    def action_fail(self):
        self.init()
        self._data["code"] = 1013
        self._data["msg"] = '操作失败'

        return self._data

    @property
    def not_found(self):
        self.init()
        self._data["code"] = 1014
        self._data["msg"] = '未找到数据'

        return self._data

    @property
    def question_already_answered(self):
        self.init()
        self._data["code"] = 1015
        self._data["msg"] = '问题已经回答'

        return self._data

    @property
    def user_already_registered(self):
        self.init()
        self._data["code"] = 1016
        self._data["msg"] = '用户已注册，请不要重复注册！'

        return self._data

    @property
    def operation_too_frequent(self):
        self.init()
        self._data["code"] = 1017
        self._data["msg"] = '操作太频繁，请稍后再试！'

        return self._data

    def operation_failed(self, msg, data=None):
        self.init()
        self._data["code"] = 1018
        self._data["data"] = data or []
        self._data["msg"] = msg or '当前操作失败，请稍后再试！'

        return self._data

    def format_failed(self, msg):
        self.init()
        self._data["code"] = 1019
        self._data["msg"] = msg or '转换文件格式失败，请稍后再试！'

        return self._data

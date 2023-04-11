#!/usr/bin/env python3
# coding=UTF-8

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
from flask import current_app


class SendSms:

    def __init__(self):
        self.cdn = current_app.config.get("CDN")
        self.client = AcsClient(current_app.config.get("ACCESS_KEY_ID"), current_app.config.get(
            "ACCESS_SECRET"), self.cdn)

    # 默认短信模板SMS_192365145
    def send(self, phone_number, text, template_code="SMS_192530146"):
        request = CommonRequest()
        request.set_accept_format('json')
        request.set_domain('dysmsapi.aliyuncs.com')
        request.set_method('POST')
        request.set_protocol_type('https')  # https | http
        request.set_version('2017-05-25')
        request.set_action_name('SendSms')
        # 服务区
        request.add_query_param('RegionId', self.cdn)
        request.add_query_param('PhoneNumbers', phone_number)  # 手机号
        request.add_query_param('SignName', current_app.config.get(
            "SIGN_NAME"))  # 签名
        request.add_query_param('TemplateCode', template_code)  # 模板编号
        request.add_query_param(
            'TemplateParam', {"code": f'{text}'})  # 发送验证码内容

        response = self.client.do_action(request)
        response = str(response, encoding='utf-8')
        print(response)

        return response

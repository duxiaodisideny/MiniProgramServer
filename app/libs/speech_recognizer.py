#!/usr/bin/env python3
# coding=UTF-8
# -*- coding: utf-8 -*-
import http.client
import os
import json
import time

from .status_code import StatusCode
from contextlib import contextmanager
from .create_token import AccessToken


@contextmanager
def connect_manager(host):
    conn = http.client.HTTPConnection(host)
    yield conn
    conn.close()


class SpeechHandle:
    def __init__(self, appKey='', access_key_id='', access_key_secret=""):
        self.appKey = appKey
        self.access_key_secret = access_key_secret
        self.access_key_id = access_key_id
        self.sc = StatusCode()
        self.create_token()

    def create_token(self):
        if not self.access_key_secret or not self.access_key_id:
            raise Exception("access_key_secret和access_key_secret不能为空")
        self.token, expire_time = AccessToken.create_token(
            self.access_key_id, self.access_key_secret)
        print('token: %s, expire time(s): %s' % (self.token, expire_time))
        if expire_time:
            print('token有效期的北京时间：%s' %
                  (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(expire_time))))

    # 转换语音格式
    def MP32Wav(self, mp3_path, wav_path):
        os.system(
            f'ffmpeg -y -i {mp3_path} -ac 1 -ar 16000 {wav_path}')
        print(wav_path, 78787878)

    # 语音识别
    def recognizer_process(self, request, audioFile):
        # 读取音频文件
        with open(audioFile, mode='rb') as f:
            audioContent = f.read()
        host = 'nls-gateway.cn-shanghai.aliyuncs.com'
        # 设置HTTP请求头部
        httpHeaders = {
            'X-NLS-Token': self.token,
            'Content-type': 'application/octet-stream',
            'Content-Length': len(audioContent)
        }
        with connect_manager(host) as conn:
            conn.request(method='POST', url=request,
                         body=audioContent, headers=httpHeaders)
            response = conn.getresponse()
            print('Response status and response reason:')
            print(response.status, response.reason)
            body = response.read()
            try:
                print('Recognize response is:')
                body = json.loads(body)
                print(body)
                status = body['status']
                if status == 20000000:
                    result = body['result']
                    print('Recognize result: ' + result)
                    return self.sc.success(data=result)
                else:
                    print('Recognizer failed!')
                    return self.sc.operation_failed('Recognizer failed!')
            except ValueError:
                print('The response is not json format string')
                return self.sc.operation_failed('The response is not json format string')

    # 语音识别

    def run_recognizer(self, mp3_path, wav_path):
        self.MP32Wav(mp3_path, wav_path)
        if not self.appKey or not self.token:
            return self.sc.params_missing
        # 转换文件失败
        if not os.path.exists(wav_path):
            return self.sc.format_failed
        url = 'http://nls-gateway.cn-shanghai.aliyuncs.com/stream/v1/asr'
        format = 'pcm'
        sampleRate = 16000
        enablePunctuationPrediction = True
        enableInverseTextNormalization = True
        enableVoiceDetection = False
        # 设置RESTful请求参数
        request = url + '?appkey=' + self.appKey
        request = request + '&format=' + format
        request = request + '&sample_rate=' + str(sampleRate)
        if enablePunctuationPrediction:
            request = request + '&enable_punctuation_prediction=' + 'true'
        if enableInverseTextNormalization:
            request = request + '&enable_inverse_text_normalization=' + 'true'
        if enableVoiceDetection:
            request = request + '&enable_voice_detection=' + 'true'
        print('Request: ' + request)

        return self.recognizer_process(request, wav_path)

    # 语音合成
    def synthesizer_process(self, text, audioSaveFile, format, sampleRate, filename):
        host = 'nls-gateway.cn-shanghai.aliyuncs.com'
        url = 'https://' + host + '/stream/v1/tts'
        # 设置HTTPS Headers
        httpHeaders = {
            'Content-Type': 'application/json'
        }
        # 设置HTTPS Body
        body = {'appkey': self.appKey, 'token': self.token, 'text': text,
                'format': format, 'sample_rate': sampleRate}
        body = json.dumps(body)
        print('The POST request body content: ' + body)
        with connect_manager(host) as conn:
            # conn = http.client.HTTPSConnection(host)
            conn.request(method='POST', url=url,
                         body=body, headers=httpHeaders)
            # 处理服务端返回的响应
            response = conn.getresponse()
            print('Response status and response reason:')
            print(response.status, response.reason)
            contentType = response.getheader('Content-Type')
            print(contentType)
            body = response.read()
            if 'audio/mpeg' == contentType:
                with open(audioSaveFile, mode='wb') as f:
                    f.write(body)
                print('The POST request succeed!')
            else:
                print('The POST request failed: ' + str(body))
                res = str(body)
                print(res, 90909090)
                return self.sc.operation_failed(msg="合成出错了。")
        # conn.close()
            return self.sc.success(data=f"/static/MergeAudio/{filename}")

    def run_synthesizer(self, text, audioSaveFile, filename):
        # audioSaveFile: abc.mp3
        # 采样率16000
        if not self.appKey or not self.token or text is None or text == '' or not audioSaveFile:
            return self.sc.params_missing
            #

        return self.synthesizer_process(text, audioSaveFile, 'mp3', 16000, filename)


if __name__ == "__main__":
    appKey = 'PA95dNepzaluNgUr'
    token = 'd75f0450d3c14ee9a32eecaa51334ab0'
    # 服务请求地址
    # 音频文件
    audioFile = 'G:/software/project/tb-project/flask/education-ap2/education-app/app/static/updateAudio/林俐.wav'
    # mp3_path = 'G:/software/project/tb-project/flask/education-ap2/education-app/app/static/updateAudio/林俐.mp3'
    mp3_path = 'G:/software/project/tb-project/flask/education-ap2/education-app/app/static/MergeAudio/合成语音.mp3'
    merge_mp3_path = 'G:/software/project/tb-project/flask/education-ap2/education-app/app/static/MergeAudio/合成语音.mp3'
    s = SpeechHandle(appKey, token)
    status, res = s.run_recognizer(mp3_path, audioFile)
    print(status, res)

    status, res = s.run_synthesizer("这是测试的语音合成。说的人话、", merge_mp3_path)
    print(status, res)

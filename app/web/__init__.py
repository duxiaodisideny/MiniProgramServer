#!/usr/bin/env python3
# coding=UTF-8
'''
Date: 2020-11-08 01:46:12
LastEditTime: 2020-11-08 09:42:41
Description: file content
'''

from flask import Blueprint
web = Blueprint(
    'web',
    __name__,
    url_prefix='/web',
    template_folder='templates',
    static_folder='static')

from . import views  # noqa

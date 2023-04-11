#!/usr/bin/env python3
# coding=UTF-8

from flask import Blueprint

api = Blueprint('api', __name__, url_prefix='api')

from . import views  # noqa

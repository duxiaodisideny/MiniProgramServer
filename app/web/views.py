#!/usr/bin/env python3
# coding=UTF-8
from flask import request, g, render_template, jsonify  # noqa
from . import web


@web.route('/questionPage', methods=['GET', 'POST'])
def get_question_page():
    if request.method == 'GET':
        return render_template('question.html')
    elif request.method == 'POST':
        pass

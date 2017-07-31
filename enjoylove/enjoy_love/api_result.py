#coding:utf-8
from __future__ import unicode_literals
import json
from rest_framework import serializers


class ApiResult(object):

    def __init__(self, code=0, msg='', result=dict(), error=''):
        self.code = code
        self.msg = msg
        self.result = result
        self.error = error

    def to_json(self):
        json_result = {}
        json_result.update(self.__dict__)
        return json_result

    def __call__(self, *args, **kwargs):
        json_result = {}
        json_result.update(self.__dict__)
        return json_result

    def __repr__(self):
        return repr((self.code, self.msg, self.result, self.error))


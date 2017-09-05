#coding:utf-8
from __future__ import unicode_literals
from rest_framework.response import Response
import json

import rest_framework.response
from rest_framework import serializers


class ApiResult(Response):

    def __init__(self, msg='ok', code=0, result=None, error=''):
        if not result:
            result = dict()
        data = {
            "code": code,
            "msg": msg,
            "result": result,
            "error": error,
        }
        super(ApiResult, self).__init__(data=data)


    #def __repr__(self):
    #    return repr((self.code, self.msg, self.result, self.error))


class BusinessError(Response, BaseException):
    def __init__(self, msg='not ok', code=1, result=None, error=''):
        if not result:
            result = dict()
        data = {
            "code": code,
            "msg": msg,
            "result": result,
            "error": error,
        }
        super(BusinessError, self).__init__(data=data)
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

# Create your tests here.

from qiniu import Auth, put_file, etag, urlsafe_base64_encode
from django.conf import settings

class QiniuTest(TestCase):

    def upload_test(self):
        #q = Auth(settings.QINIU['access_key'], settings.QINIU['secret_key'])
        token = "PYAMUiFJfHPzG3meWILMARcIu-djqhv51a2lMO4:nom5VzDylfYxxGjRiMdgBGJKQJk=:eyJzY29wZSI6InhpYW5nbGlhbi1zbnM6bGFsYS50eHQiLCJkZWFkbGluZSI6MTUwNDQyNTk4MH0="
        localfile = '/Users/yuwhuawang/enjoylove/requirements.txt'
        key = "lala.txt"
        ret, info = put_file(token, key, localfile)
        assert ret['key'] == key
        assert ret['hash'] == etag(localfile)


if __name__ == '__main__':
    QiniuTest().upload_test()



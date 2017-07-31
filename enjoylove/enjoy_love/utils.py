#coding:utf-8
from __future__ import unicode_literals

import random

import time


def create_verify_code():
    chars = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    x = random.choice(chars), random.choice(chars), random.choice(chars), random.choice(chars)
    verifycode = "".join(x)
    return verifycode
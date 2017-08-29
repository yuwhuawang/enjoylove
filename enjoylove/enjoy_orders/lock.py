#coding:utf-8
__author__ = 'yuwhuawang'
__created__ = '2017/08/29 23:26'

import redis
import uuid

from django.conf import settings


class RedisLock(object):

    _strict = redis.StrictRedis(
        host=settings.LOCK_REDIS_HOST,
        port=settings.LOCK_REDIS_PORT,
        db=settings.LOCK_REDIS_DB)

    _lua_acquire = _strict.register_script(
        '''
        local lock = redis.call('GET', KEYS[1])
        if lock then
            return false
        else
            redis.call('SET', KEYS[1], ARGV[1])
            redis.call('EXPIRE', KEYS[1], ARGV[2])
            return true
        end
        ''')

    _lua_release = _strict.register_script(
        '''
        local lock = redis.call('GET', KEYS[1])
        if (lock and lock == ARGV[1]) then
            redis.call('DEL', KEYS[1])
            return true
        else
            return false
        end
        ''')

    def __init__(self, key, timeout=settings.LOCK_TIMEOUT):
        self.key = key
        self.uuid = uuid.uuid4().get_hex()
        self.timeout = timeout

    def acquire(self):
        ret = self._lua_acquire(keys=[self.key],
                                args=[self.uuid, self.timeout])
        return True if ret else False

    def release(self):
        return self._lua_release(keys=[self.key], args=[self.uuid])
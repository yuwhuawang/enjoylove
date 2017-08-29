#coding:utf-8
#Author: Yuwhuawang
import hashlib
import json

import time
import urllib
import uuid

import datetime

from utils import safe_utf8, Httplib2Mixin, XmlUtil


class WeixinBaseUtil(object):
    unifiedorder_url = 'https://api.mch.weixin.qq.com/pay/unifiedorder'
    query_order_url = 'https://api.mch.weixin.qq.com/pay/orderquery'
    access_token_url = 'https://api.weixin.qq.com/cgi-bin/token'
    user_info_url = 'https://api.weixin.qq.com/cgi-bin/user/info'

    native_url_format = 'weixin://wxpay/bizpayurl?sign=%(sign)s&' \
                        'appid=%(app_id)s&mch_id=%(mch_id)s&product_id=%(product_id)s&' \
                        'time_stamp=%(timestamp)s&nonce_str=%(noncestr)s'

    unifiedorder_sign_keys = (
        'appid', 'mch_id', 'nonce_str', 'body', 'out_trade_no',
        'total_fee', 'spbill_create_ip', 'notify_url', 'trade_type',
        'product_id',
    )

    native_url_sign_keys = (
        'app_id', 'mch_id', 'product_id', 'timestamp', 'noncestr')

    native_sign_keys = (
        'appid', 'mch_id', 'nonce_str', 'prepay_id', 'result_code',
        'err_code_des',
    )
    native_verify_keys = (
        'appid', 'openid', 'mch_id', 'is_subscribe', 'nonce_str', 'product_id',
    )

    app_id = 'wxc3b218fb0687a6ea'
    app_key = 'hellptgstarstaronetwothree123321'
    app_secret = '32f6a178640b792f5c6db279a14477f3'
    mch_id = '10010917'
    notify_url = 'https://play.putaogame.com/api/v1/notify/weixin/'
    deliver_url = 'http://'
    trade_type = 'NATIVE'
    charset = 'UTF-8'
    default_padding = '&key=hellptgstarstaronetwothree123321'

    def sign(self, data, interest_keys=None, padding=None):
        message = self.construct_message(data, interest_keys,
                                         padding=padding)
        sign = hashlib.md5(message).hexdigest()
        return sign.upper()

    def verify(self, data, expect_sign, interest_keys=None):
        sign = self.sign(data, interest_keys, padding=self.default_padding)
        return sign == expect_sign

    def construct_message(self, data, interest_keys=None, padding=None):
        if interest_keys:
            if any(map(lambda x: x not in data, interest_keys)):
                raise Exception('Missing parameters')

            message = '&'.join([safe_utf8('%s=%s' % (k, v)) for k, v in
                                sorted(data.items()) if k in interest_keys
                                and v])
        else:
            message = '&'.join([safe_utf8('%s=%s' % (k, v)) for k, v in
                                sorted(data.items())])
        if padding:
            message = message + padding
        return message


class WeixinUtil(WeixinBaseUtil, Httplib2Mixin):

    def __init__(self, img_type='JPEG'):
        self.img_type = img_type

    def create_static_native_qrcode(self, product_id):
        return self.build_qrcode(self.build_native_url(product_id))

    def create_dynamic_native_qrcode(self, trade_no, body, fee, ip):
        ret, data = self.create_unifiedorder(trade_no, body, fee, ip)
        if not ret:
            raise Exception('Failed to create dynamic native url for weixin')

        return self.build_qrcode(data['code_url']), data



    def build_native_url(self, product_id):
        data = {}
        data['product_id'] = product_id
        data['app_id'] = self.app_id
        data['mch_id'] = self.mch_id
        data['timestamp'] = int(time.time())
        data['noncestr'] = uuid.uuid4().get_hex()
        data['sign'] = self.sign_native_url(data)

        return self.native_url_format % (data)

    def create_native_response(self, code, msg, prepay_id):
        data = {}
        data['return_code'] = 'SUCCESS'
        data['appid'] = self.app_id
        data['mch_id'] = self.mch_id
        data['nonce_str'] = uuid.uuid4().get_hex()
        data['prepay_id'] = prepay_id
        data['result_code'] = code
        data['err_code_des'] = msg
        data['sign'] = self.sign_native_response(data)

        return data

    def verify_native_request(self, raw_data):
        data = XmlUtil.xml_to_dict(raw_data)
        return (self.verify_native(data, data['sign']),
                data.get('product_id', None))

    def create_unifiedorder(self, trade_no, body, fee, ip):
        params = self.create_unifiedorder_params(
            trade_no, trade_no, body, fee, ip)

        headers = {'Content-Type': 'application/xml'}
        for i in range(3):
            try:
                h, b = self.request(
                    self.unifiedorder_url, 'POST', params, headers)

                if h and h.status == 200:
                    return self.verify_unifiedorder_response(b)
            except:
                continue
        else:
            raise Exception('Weixin server unifiedorder not respond')

    def query_order(self, transaction_id):
        params = self.create_query_params(transaction_id)

        headers = {'Content-Type': 'application/xml'}
        try:
            h, b = self.request(
                self.query_order_url, 'POST', params, headers)

            if h and h.status == 200:
                return XmlUtil().xml_to_dict(b)
        except:
            return None

    def get_user_info(self, openid):
        params = self.create_user_info_params(openid)

        url = '{}?{}'.format(self.user_info_url, urllib.urlencode(params))
        try:
            h, b = self.request(url)

            if h and h.status == 200:
                return json.loads(b)
        except:
            return None

    def get_access_token(self):
        params = self.create_access_token_params()

        url = '{}?{}'.format(self.access_token_url, urllib.urlencode(params))
        try:
            h, b = self.request(url)

            if h and h.status == 200:
                return json.loads(b)
        except:
            return None

    def verify_unifiedorder_response(self, raw_data):
        data = XmlUtil.xml_to_dict(raw_data)
        if data.get('return_code', None) != 'SUCCESS':
            raise Exception('Weixin server unifiedorder not respond')

        if not self.verify(data, data['sign'],
                           [k for k in data if k != 'sign']):
            raise Exception('Unifiedorder invalid signature')

        return ((data['return_code'] == 'SUCCESS' and
                 data['result_code'] == 'SUCCESS'),
                data)

    def create_unifiedorder_params(self, product_id, trade_no, body, fee, ip):
        data = {}
        data['appid'] = self.app_id
        data['mch_id'] = self.mch_id
        data['nonce_str'] = uuid.uuid4().get_hex()
        data['body'] = safe_utf8(body)
        data['out_trade_no'] = trade_no
        data['total_fee'] = fee
        data['spbill_create_ip'] = ip
        data['notify_url'] = self.notify_url
        data['trade_type'] = self.trade_type
        data['product_id'] = product_id

        data['sign'] = self.sign(data, padding=self.default_padding)

        return XmlUtil.dict_to_xml(data)

    def create_query_params(self, transaction_id):
        data = {}
        data['appid'] = self.app_id
        data['mch_id'] = self.mch_id
        data['nonce_str'] = uuid.uuid4().get_hex()
        data['transaction_id'] = transaction_id

        data['sign'] = self.sign(data, padding=self.default_padding)

        return XmlUtil.dict_to_xml(data)

    def create_user_info_params(self, openid):
        data = {}
        data['access_token'] = self.get_last_access_token()
        data['openid'] = openid

        return data

    def create_access_token_params(self):
        data = {}
        data['grant_type'] = 'client_credential'
        data['appid'] = self.app_id
        data['secret'] = self.app_secret

        return data

    def get_last_access_token(self):
        from models import WeixinToken

        try:
            wt = WeixinToken.objects.filter(
                expires_in__gt=datetime.datetime.now()).\
                order_by('-modified')[0]
            token = wt.token
        except IndexError:
            data = self.get_access_token()
            if not data:
                return None
            token, expires_in = data['access_token'], data['expires_in']
            expires_in = datetime.datetime.now() + \
                datetime.timedelta(seconds=expires_in)
            WeixinToken.objects.create(token=token, expires_in=expires_in)

        return token

    def sign_native_url(self, data):
        return self.sign(data, self.native_url_sign_keys)

    def sign_native(self, data):
        return self.sign(data, self.native_sign_keys)

    def verify_native(self, data, sign):
        return self.verify(data, sign, self.native_request_keys)


class WeixinNotifyUtil(WeixinBaseUtil):

    def __init__(self, notify_data, source='weixin'):
        self.notify_data = notify_data
        self.source = source

    def isValid(self):
        data = self.notify_data
        return self.verify(data, data['sign'],
                           [k for k in data if k != 'sign'])

    def getTradeInfo(self):
        data = self.notify_data

        obj = {}
        obj['source'] = self.source
        obj['uuid'] = uuid.uuid4().get_hex()
        obj['order_sn'] = data['out_trade_no']
        obj['outer_order_sn'] = data['transaction_id']
        obj['trade_date'] = datetime.datetime.strptime(data['time_end'],
                                                       '%Y%m%d%H%M%S')
        obj['status'] = data['return_code'] == 'SUCCESS' and \
            data['result_code'] == 'SUCCESS'

        return obj

    def getSuccessMessage(self):
        return XmlUtil.dict_to_xml({'return_code': 'SUCCESS'})

    def getErrorMessage(self):
        return XmlUtil.dict_to_xml({'return_code': 'FAILURE'})

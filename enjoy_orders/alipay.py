#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Peter Peng


import hashlib
import json
import lxml.etree as ET
import urllib
import uuid

from datetime import datetime, timedelta

from core.utils import RSAUtil
from core.utils import Httplib2Mixin


def safe_utf8(s):
    return isinstance(s, unicode) and s.encode('utf-8') or str(s)


class XmlUtil(object):

    @staticmethod
    def dict_to_xml(data):
        root = ET.Element('xml')
        for k, v in data.items():
            sub = ET.SubElement(root, k)
            text = safe_utf8(v).decode('utf-8')
            if k == 'body':
                sub.text = ET.CDATA(text)
            else:
                sub.text = text

        return ET.tostring(root, encoding='utf-8')

    @staticmethod
    def xml_to_dict(data):
        obj = {}
        root = ET.fromstring(data)
        for child in root:
            if child.tag == 'request':
                continue
            elif child.tag == 'response':
                params = child.getchildren()[0]
                for param in params:
                    obj[param.tag] = param.text
            else:
                obj[child.tag] = child.text

        return obj


ALIAPY_SIGN_PRIVATE_KEY = '''-----BEGIN RSA PRIVATE KEY-----
MIICXAIBAAKBgQDB0uHA93Cm0aO9s/bpzlblHQItxPlFQ6kw/wmS1IipUQMdO/B+
h34/zA3B29/4HEykXPbhcIuFmzvlUdFadoAHB0aXHGn+KB5KmQOhvvV5AILe8DJy
b8z+NH0mTY1lMNsgcTVRtAqcmhKtWQakClFupQMJO0IlzpzecCWQV0HocwIDAQAB
AoGAbDU7a+u4rKllbMdIFgfoY0jqqnrJX24CyyPXSG33Te+4eV25SiqCxUM6evwx
8eZ6s1hjTED048Zijgg7hPGbT1aPN+b0V4odTbrOdN7/d3pBKUXZSpiAfjSxTONZ
GbSDw2QlLx3V51XqoIYW5u9AxHtpxIapgTAxmeMGxyFW8mECQQD8Pkr3nLXvqT+D
8RxeOa65+E3TgyPrhtd5TeNzE3tGX2AUvfJosGLTfWEdzrOFiZLi9vpw/SN3gVBf
R7LMR4x9AkEAxLXbiRtSQDQrdn6xukM7P5FmKI+74OseGlEkieMG1/IN8VOqZCRe
sTcTTNOZCxDhEwbTFxSev99lSLJbpyWLrwJAJX3ozKcJT8b7PtQ+oC64rsGeZ7rN
Qvu22Tvfe8JAh3QzpsGY30CgX8j5/2Eyw71wDLYjAVpOxDt/Q7o3dC+KTQJATvzn
Zqq94GISgcZl/3E3vVLZPrhYrPw8Xjzu+x9ahCQCTUFXTlb8XxTKfzMIZVUly8oV
wVLaXBmMRiC4hOmiqQJBAI0fq+bWmsLP1MFhpP2vRRw6Jwl1qWql/pesuSwU4H3T
3gyfebPmxYAtaL8wF67jhTEpaTm+Y3Ah50FyESxkubE=
-----END RSA PRIVATE KEY-----
'''


ALIAPY_SIGN_PUBLIC_KEY = '''-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDB0uHA93Cm0aO9s/bpzlblHQIt
xPlFQ6kw/wmS1IipUQMdO/B+h34/zA3B29/4HEykXPbhcIuFmzvlUdFadoAHB0aX
HGn+KB5KmQOhvvV5AILe8DJyb8z+NH0mTY1lMNsgcTVRtAqcmhKtWQakClFupQMJ
O0IlzpzecCWQV0HocwIDAQAB
-----END PUBLIC KEY-----
'''

ALIPAY_VERIFY_PUBLICK_KEY = '''-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCnxj/9qwVfgoUh/y2W89L6BkR
AFljhNhgPdyPuBV64bfQNN1PjbCzkIM6qRdKBoLPXmKKMiFYnkd6rAoprih3/Pr
QEB/VsW8OoM8fxn67UDYuyBTqA23MML9q1+ilIZwBC2AQ2UBVOrFXfFl75p6/B5
KsiNG9zpgmLCUYuLkxpLQIDAQAB
-----END PUBLIC KEY-----
'''


class AlipayQrcodeBaseUtil(object):

    pid = '2088211521798044'
    key = 'gz0fp9h9i561r7eun494bunutda0mj78'
    service_name = 'alipay.mobile.qrcode.manage'
    api_url = 'https://mapi.alipay.com/gateway.do'
    notify_url = 'https://play.putaogame.com/api/v1/notify/alipay/'

    def sign(self, data):
        message = self.construct_message(data, padding=self.key)
        sign = hashlib.md5(message).hexdigest()
        return sign

    def verify(self, data, sign, ignore_keys=None):
        message = self.construct_message(
            data, ignore_keys=ignore_keys, padding=self.key)
        return sign == hashlib.md5(message).hexdigest()

    def construct_message(self, data, interest_keys=None,
                          ignore_keys=None, padding=None):
        ignore_keys = ignore_keys or []
        if interest_keys:
            if any(map(lambda x: x not in data, interest_keys)):
                raise Exception('Missing parameters')

            message = '&'.join([safe_utf8('%s=%s' % (k, v)) for k, v in
                                sorted(data.items()) if k in interest_keys
                                and k not in ignore_keys and v])
        else:
            message = '&'.join([safe_utf8('%s=%s' % (k, v)) for k, v in
                                sorted(data.items())
                                if k not in ignore_keys])
        if padding:
            message = message + padding
        return message


class AlipayQrcodeUtil(AlipayQrcodeBaseUtil, Httplib2Mixin):

    def create_dynamic_qrcode(self, product_id, product_name, fee):
        return self.add_new_qrcode(product_id, product_name, fee)

    def add_new_qrcode(self, product_id, product_name, fee):
        data = {}

        # basic parameters
        data['service'] = self.service_name
        data['partner'] = self.pid
        data['_input_charset'] = 'utf-8'
        data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # business parameters
        data['method'] = 'add'
        data['biz_type'] = '10'

        # biz data
        biz_data = {}
        biz_data['trade_type'] = '1'
        biz_data['need_address'] = 'F'
        biz_data['goods_info'] = self.build_goods(
            product_id, product_name, fee)
        biz_data['notify_url'] = self.notify_url
        data['biz_data'] = json.dumps(biz_data)

        data['sign'] = self.sign(data)
        data['sign_type'] = 'MD5'

        url = '%s?%s' % (self.api_url, urllib.urlencode(data))
        for i in range(3):
            try:
                h, b = self.request(url)

                if h and h.status == 200:
                    resp_data = XmlUtil.xml_to_dict(b)
                    if self.verify(
                            resp_data, resp_data['sign'],
                            ignore_keys=['sign_type', 'sign', 'is_success']):
                        return resp_data['qrcode_img_url'], resp_data
                    else:
                        continue
            except:
                pass

        raise Exception('Weixin Server not responable')

    def build_goods(self, product_id, product_name, fee):
        price = '%.2f' % (fee / 100.0)
        goods = {}
        goods['id'] = str(product_id)
        goods['name'] = product_name
        goods['price'] = price
        start_date = datetime.now() - timedelta(days=1)
        end_date = start_date + timedelta(days=31)
        goods['expiry_date'] = '{}|{}'.format(
            start_date.strftime('%Y-%m-%d %H:%M:%S'),
            end_date.strftime('%Y-%m-%d %H:%M:%S'))
        return goods


class AlipayQrcodeNotifyUtil(AlipayQrcodeBaseUtil):

    def __init__(self, notify_data, source='alipay'):
        self.notify_data = notify_data
        self.source = source

    def isValid(self):
        data = self.notify_data
        return self.verify(data, data['sign'],
                           ignore_keys=['sign', 'sign_type'])

    def getTradeInfo(self):
        from payment.models import Receipt

        data = XmlUtil.xml_to_dict(self.notify_data['notify_data'])

        obj = {}
        obj['source'] = self.source
        obj['uuid'] = uuid.uuid4().get_hex()
        obj['order_sn'] = Receipt.get_order_sn_by_alipay_qrcode(
            data['qrcode'])
        obj['outer_order_sn'] = data['trade_no']
        obj['status'] = data['trade_status'] == 'TRADE_SUCCESS'
        obj['trade_date'] = data['gmt_payment']

        return obj

    def getSuccessMessage(self):
        return 'success'

    def getErrorMessage(self):
        return 'fail'


class AlipayMobileBaseUtil(object):

    pid = '2088211521798044'
    service_name = 'mobile.securitypay.pay'
    notify_url = 'https://play.putaogame.com/api/v1/notify/alipay_mobile/'
    sign_key = ALIAPY_SIGN_PRIVATE_KEY
    verify_key = ALIPAY_VERIFY_PUBLICK_KEY

    def rsaSign(self, message):
        return RSAUtil(None, self.sign_key).sign(message)

    def rsaVerify(self, data):
        sign = data.get('sign')

        message = '&'.join([safe_utf8(u'%s=%s' % (k, v)) for k, v in
                            sorted(data.items())
                            if v and k not in ['sign', 'sign_type']])
        return RSAUtil(self.verify_key, None).verify(
            message.decode('utf-8'), sign)


class AlipayMobileOrderUtil(AlipayMobileBaseUtil):

    def createPayInfo(self, order_sn, subject, amount):
        subject = safe_utf8(subject)
        params = {}
        params['service'] = self.service_name
        params['partner'] = self.pid
        params['_input_charset'] = 'utf-8'
        params['notify_url'] = self.notify_url

        params['out_trade_no'] = order_sn
        params['subject'] = subject
        params['payment_type'] = 1
        params['seller_id'] = 'hr@putaogame.com'
        params['total_fee'] = amount
        params['body'] = subject

        message = '&'.join([safe_utf8('%s="%s"' % (k, v)) for k, v in
                            sorted(params.items())])

        sign = urllib.quote(self.rsaSign(message), safe='')
        message += '&sign="%s"&sign_type="RSA"' % sign

        return message


class AlipayMobileNotifyUtil(AlipayMobileBaseUtil):

    def __init__(self, notify_data, source='alipay_mobile'):
        self.notify_data = notify_data
        self.source = source

    def isValid(self):
        return self.rsaVerify(self.notify_data)

    def getTradeInfo(self):
        if not self.isValid():
            raise Exception('Invalid notify data')

        data = self.notify_data

        obj = {}
        obj['source'] = self.source
        obj['uuid'] = data['notify_id']
        obj['order_sn'] = data['out_trade_no']
        obj['outer_order_sn'] = data['trade_no']
        obj['status'] = data['trade_status'] in \
            ['TRADE_SUCCESS', 'TRADE_FINISHED']
        obj['trade_date'] = datetime.now()

        return obj

    def getSuccessMessage(self):
        return 'success'

    def getErrorMessage(self):
        return 'fail'


class AlipayMobileChargeUtil(AlipayMobileOrderUtil):
    """
    使用支付宝充值葡萄币
    """
    notify_url = 'https://play.putaogame.com/api/v1/wallet/callback/alipay_mobile/'

#coding:utf-8
import urllib
import uuid

import gevent
import socket
import httplib2
import lxml.etree as ET
import requests
from django.conf import settings
from models import Notify
from tasks import processNotify

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
            obj[child.tag] = child.text

        return obj


def is_module_patched_by_gevent(modulename):
    try:
        from gevent.monkey import is_module_patched
        return is_module_patched(modulename)
    except ImportError:
        pass

    try:
        from gevent.monkey import saved
        return modulename in saved
    except ImportError:
        return False


def get_client_ip(request):
    if 'HTTP_X_REAL_IP' in request.META:
        ip = request.META['HTTP_X_REAL_IP']
    elif 'HTTP_X_FORWARDED_FOR' in request.META:
        ip = request.META['HTTP_X_FORWARDED_FOR'].split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip.strip() or ''


class Httplib2Mixin(object):

    is_gevent_patched = is_module_patched_by_gevent('socket')

    def request(self, *args, **kwargs):
        h, b = None, ""
        if self.is_gevent_patched:
            client = httplib2.Http(disable_ssl_certificate_validation=True)
            with gevent.Timeout(settings.HTTPLIB2_REQUEST_TIMEOUT):
                h, b = client.request(*args, **kwargs)
        else:
            client = httplib2.Http(
                disable_ssl_certificate_validation=True,
                timeout=settings.HTTPLIB2_REQUEST_TIMEOUT)
            try:
                h, b = client.request(*args, **kwargs)
            except socket.timeout:
                pass

        return h, b


def persistNotify(data, source):
    info = getTradeInfo(data, source)
    info['status'] = info['status'] and 'success' or 'failure'
    try:
        notify = Notify.objects.get(uuid=info['uuid'])
        if info['status'] == 'success':
            notify.order_sn = info['order_sn']
            notify.outer_order_sn = info['outer_order_sn']
            notify.status = info['status']
            notify.trade_date = info['trade_date']
            notify.uuid = info['uuid']
            notify.source = info['source']
            notify.save()
    except Notify.DoesNotExist:
        notify = Notify(**info)
        notify.save()

    return notify


def getTradeInfo(data, source):

    obj = {}
    obj['source'] = source
    obj['uuid'] = uuid.uuid4().get_hex()
    obj['outer_order_sn'] = data['out_trade_no']
    obj['status'] = data['result_code'] == 'SUCCESS'
    obj['trade_date'] = data['time_end']

    return obj


def delayProcessNotify(self, notify):
    processNotify.delay(notify.uuid)


class HttpUtil(object):

    def get(self, url, data):
        if isinstance(data, dict):
            data = urllib.urlencode(data)
        return requests.get('%s?%s' % (url, data)).content

    def post(self, url, data):
        if isinstance(data, dict):
            data = urllib.urlencode(data)
        return requests.post(url, data).content


httputil = HttpUtil()
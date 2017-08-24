#coding:utf-8
import gevent
import socket
import httplib2
import lxml.etree as ET
from django.conf import settings

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
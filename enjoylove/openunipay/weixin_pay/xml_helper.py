#coding:utf-8
from __future__ import unicode_literals
from xml.dom.minidom import getDOMImplementation
from xml.etree import ElementTree

from xlrd.xlsx import ET

import lxml.etree as ET1

from openunipay.util.random_helper import safe_utf8 as a

from enjoylove.openunipay.util.random_helper import safe_utf8

_xmldom_impl = getDOMImplementation()

def dict_to_xml(valueDict):
    doc = _xmldom_impl.createDocument(None, 'xml', None)
    topElement = doc.documentElement
    for (key, value) in valueDict.items():
        element = doc.createElement(key)
        element.appendChild(doc.createTextNode(str(value)))
        topElement.appendChild(element)
    return topElement.toxml()

def xml_to_dict(xmlContent):
    result = {}
    root = ElementTree.fromstring(xmlContent)
    for child in root:
        result[child.tag] = child.text
    return result


class XmlUtil(object):

    @staticmethod
    def dict_to_xml(data):
        root = ET1.Element('xml')
        for k, v in data.items():
            sub = ET1.SubElement(root, k)
            text = safe_utf8(v).decode('utf-8')
            if k == 'body':
                sub.text = ET.CDATA(text)
            else:
                sub.text = text

        return ET1.tostring(root, encoding='utf-8')

    @staticmethod
    def xml_to_dict(data):
        obj = {}
        root = ET1.fromstring(data)
        for child in root:
            obj[child.tag] = child.text

        return obj
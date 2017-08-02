# coding:utf-8
from __future__ import unicode_literals
import os
from django.conf import settings
import requests
import datetime
import hashlib, base64

__author__ = 'yuwhuawang'
__created__ = '2017/08/02 20:24'


def gen_sig_parameter():
    now = datetime.datetime.now()
    now_text = now.strftime("%Y%m%d%H%M%S")
    org_text = settings.SMS_ACCOUNTSID + settings.SMS_AUTHTOKEN + now_text
    m2 = hashlib.md5()
    m2.update(org_text)
    return m2.hexdigest()


def gen_auth_header():
    now = datetime.datetime.now()
    now_text = now.strftime("%Y%m%d%H%M%S")
    org_text = "{}:{}".format(settings.SMS_ACCOUNTSID, now_text)
    return base64.b64encode(org_text)


def send_sms(version_code, mobile):
    url = """{ApiURL}/{SoftVersion}/Accounts/{accountSid}/{function}/{operation}?sig={SigParameter}""" \
        .format(ApiURL=settings.SMS_APIURL, SoftVersion=settings.SMS_VERSION, accountSid=settings.SMS_ACCOUNTSID,
                function=settings.SMS_FUNCTION, operation=settings.SMS_OPERATION, SigParameter=gen_sig_parameter())
    data = {
        "templateSMS": {
            "appId": settings.SMS_APPID,
            "param": version_code,
            "templateId": settings.SMS_TEMPLATE_ID,
            "to": mobile
        }
    }

    headers = {"Accept": "application/json",
               "Content-Type": "application/json;charset=utf-8",
               "Authorization": gen_auth_header()}

    r = requests.post(url, data=data, headers=headers)
    print r


# -*- coding: UTF-8 -*-
#
# 具体定义和参数说明参考 云之讯REST开发者文档 .docx
#
import base64
import datetime
import urllib2
import hashlib


# 返回签名
def getSig(accountSid, accountToken, timestamp):
    sig = accountSid + accountToken + timestamp
    m2 = hashlib.md5()
    m2.update(sig)
    return m2.hexdigest().upper()


# 生成授权信息
def getAuth(accountSid, timestamp):
    src = accountSid + ":" + timestamp
    return base64.encodestring(src).strip()


# 发起http请求
def urlOpen(req, data=None):
    try:
        res = urllib2.urlopen(req, data)
        data = res.read()
        res.close()
    except urllib2.HTTPError, error:
        data = error.read()
        error.close()
    print data
    return data


# 生成HTTP报文
def createHttpReq(req, url, accountSid, timestamp, responseMode, body):
    req.add_header("Authorization", getAuth(accountSid, timestamp))
    if responseMode:
        req.add_header("Accept", "application/" + responseMode)
        req.add_header("Content-Type", "application/" + responseMode + ";charset=utf-8")
    if body:
        req.add_header("Content-Length", len(body))
        req.add_data(body)
    return req


# 参数意义说明
# accountSid 主账号
# accountToken 主账号token
# clientNumber 子账号
# appId 应用的ID
# clientType 计费方式。0  开发者计费；1 云平台计费。默认为0.
# charge 充值或回收的金额
# friendlyName 昵称
# mobile 手机号码
# isUseJson 是否使用json的方式发送请求和结果。否则为xml。
# start 开始的序号，默认从0开始
# limit 一次查询的最大条数，最小是1条，最大是100条
# responseMode 返回数据个格式。"JSON" "XML"
# chargeType  0 充值；1 回收。
# fromClient 主叫的clientNumber
# toNumber 被叫的号码
# toSerNum 被叫显示的号码
# verifyCode 验证码内容，为数字和英文字母，不区分大小写，长度4-8位
# displayNum 被叫显示的号码
# templateId 模板Id
class RestAPI:
    HOST = "https://api.ucpaas.com"
    PORT = ""
    SOFTVER = "2014-06-30"
    JSON = "json"
    XML = "xml"

    # 主账号信息查询
    # accountSid  主账号ID
    # accountToken 主账号的Token
    def getAccountInfo(self, accountSid, accountToken, isUseJson=True):
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y%m%d%H%M%S")
        signature = getSig(accountSid, accountToken, timestamp)
        url = self.HOST + ":" + self.PORT + "/" + self.SOFTVER + "/Accounts/" + accountSid + "?sig=" + signature

        if isUseJson == True:
            responseMode = self.JSON
        else:
            responseMode = self.XML

        req = urllib2.Request(url)
        return urlOpen(createHttpReq(req, url, accountSid, timestamp, responseMode, None))

    # 申请client账号
    # accountSid  主账号ID
    # accountToken 主账号的Token
    # appId 应用ID
    # clientType 计费方式。0  开发者计费；1 云平台计费。默认为0.
    # charge 充值的金额
    # friendlyName 昵称
    # mobile 手机号码
    def applyClient(self, accountSid, accountToken, appId, clientType, charge, friendlyName, mobile, isUseJson=True):
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y%m%d%H%M%S")
        signature = getSig(accountSid, accountToken, timestamp)
        url = self.HOST + ":" + self.PORT + "/" + self.SOFTVER + "/Accounts/" + accountSid + "/Clients?sig=" + signature

        if isUseJson == True:
            body = '{"client":{"appId":"%s","clientType":"%s","charge":"%s","friendlyName":"%s","mobile":"%s"}}' \
                   % (appId, clientType, charge, friendlyName, mobile)
            responseMode = self.JSON
        else:
            body = '<?xml version="1.0" encoding="utf-8"?>\
					<client>\
						<appId>%s</appId>\
						<clientType>%s</clientType>\
						<charge>%s</charge>\
						<friendlyName>%s</friendlyName>\
						<mobile>%s</mobile>\
					</client>\
					' % (appId, clientType, charge, friendlyName, mobile)
            responseMode = self.XML

        req = urllib2.Request(url)
        return urlOpen(createHttpReq(req, url, accountSid, timestamp, responseMode, body))

    # 释放client账号
    # accountSid  主账号ID
    # accountToken 主账号的Token
    # clientNumber 子账号
    # appId 应用ID
    def ReleaseClient(self, accountSid, accountToken, clientNumber, appId, isUseJson=True):
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y%m%d%H%M%S")
        signature = getSig(accountSid, accountToken, timestamp)
        url = self.HOST + ":" + self.PORT + "/" + self.SOFTVER + "/Accounts/" + accountSid + "/dropClient?sig=" + signature

        if isUseJson == True:
            body = '{"client":{"clientNumber":"%s","appId":"%s"}}' % (clientNumber, appId)
            responseMode = self.JSON
        else:
            body = '<?xml version="1.0" encoding="utf-8"?>\
					<client>\
						<clientNumber>%s</clientNumber>\
						<appId>%s</appId >\
					</client>\
					' % (clientNumber, appId)
            responseMode = self.XML

        req = urllib2.Request(url)
        return urlOpen(createHttpReq(req, url, accountSid, timestamp, responseMode, body))

    # 获取client账号
    # accountSid  主账号ID
    # accountToken 主账号的Token
    # appId 应用ID
    # start 开始的序号，默认从0开始
    # limit 一次查询的最大条数，最小是1条，最大是100条
    def getClientList(self, accountSid, accountToken, appId, start, limit, isUseJson=True):
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y%m%d%H%M%S")
        signature = getSig(accountSid, accountToken, timestamp)
        url = self.HOST + ":" + self.PORT + "/" + self.SOFTVER + "/Accounts/" + accountSid + "/clientList?sig=" + signature

        if isUseJson == True:
            body = '{"client":{"appId":"%s","start":"%s","limit":"%s"}}' % (appId, start, limit)
            responseMode = self.JSON
        else:
            body = "<?xml version='1.0' encoding='utf-8'?>\
					<client>\
						<appId>%s</appId>\
						<start>%s</start>\
						<limit>%s</limit>\
					</client>\
					" % (appId, start, limit)
            responseMode = self.XML

        req = urllib2.Request(url)
        return urlOpen(createHttpReq(req, url, accountSid, timestamp, responseMode, body))

    # client信息查询 注意为GET方法
    # accountSid  主账号ID
    # accountToken 主账号的Token
    # appId 应用ID
    # clientNumber 子账号
    def getClientInfo(self, accountSid, accountToken, appId, clientNumber, isUseJson=True):
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y%m%d%H%M%S")
        signature = getSig(accountSid, accountToken, timestamp)
        url = self.HOST + ":" + self.PORT + "/" + self.SOFTVER + "/Accounts/" + accountSid + "/Clients?sig=" + signature \
              + "&clientNumber=" + clientNumber + "&appId=" + appId

        if isUseJson == True:
            body = '{"client":{"appId":"%s","clientNumber":"%s"}}' % (appId, clientNumber)
            responseMode = self.JSON
        else:
            responseMode = self.XML

        req = urllib2.Request(url)
        return urlOpen(createHttpReq(req, url, accountSid, timestamp, responseMode, None))

    # client信息查询(mobile方式) 注意为GET方法
    # accountSid  主账号ID
    # accountToken 主账号的Token
    # appId 应用ID
    # mobile 手机号
    def getClientInfoByMobile(self, accountSid, accountToken, appId, mobile, isUseJson=True):
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y%m%d%H%M%S")
        signature = getSig(accountSid, accountToken, timestamp)
        url = self.HOST + ":" + self.PORT + "/" + self.SOFTVER + "/Accounts/" + accountSid + "/ClientsByMobile?sig=" + signature \
              + "&mobile=" + mobile + "&appId=" + appId

        if isUseJson == True:
            body = '{"client":{"appId":"%s","mobile":"%s"}}' % (appId, mobile)
            responseMode = self.JSON
        else:
            responseMode = self.XML

        req = urllib2.Request(url)
        return urlOpen(createHttpReq(req, url, accountSid, timestamp, responseMode, None))

    # 应用话单下载
    # accountSid 主账号ID
    # accountToken 主账号Token
    # appId 应用ID
    # date 枚举类型 day 代表前一天的数据（从00:00 – 23:59）；week代表前一周的数据(周一 到周日)；month表示上一个月的数据
    def getBillList(self, accountSid, accountToken, appId, date, isUseJson=True):
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y%m%d%H%M%S")
        signature = getSig(accountSid, accountToken, timestamp)
        url = self.HOST + ":" + self.PORT + "/" + self.SOFTVER + "/Accounts/" + accountSid + "/billList?sig=" + signature

        if isUseJson == True:
            body = '{"appBill":{"appId":"%s","date":"%s"}}' % (appId, date)
            responseMode = self.JSON
        else:
            body = "<?xml version='1.0' encoding='utf-8'?>\
					<appBill>\
						<appId>%s</appId>\
						<date>%s</date>\
					</appBill>\
					" % (appId, date)
            responseMode = self.XML

        req = urllib2.Request(url)
        return urlOpen(createHttpReq(req, url, accountSid, timestamp, responseMode, body))

    # 通用话单下载URL
    # def getAccountInfo(accountSid,accountToken,isUseJson=True):
    # now = datetime.datetime.now()
    # timestamp = now.strftime("%Y%m%d%H%M%S")
    # signature = getSig(accountSid,accountToken,timestamp)
    # url = self.HOST + ":" + self.PORT + "/" + self.SOFTVER + "/Accounts/" + accountSid + "?sig=" + signature

    # req = urllib2.Request(url)
    # self.setHttpHeader(req)
    # req.add_header("Authorization", getAuth(accountSid,timestamp))
    # if isUseJson == True:
    # responseMode = self.JSON
    # else:
    # responseMode = self.XML
    # req.add_header("Accept","application/"+responseMode)

    # return urlOpen(req)

    # client话单下载
    # accountSid 主账号ID
    # accountToken 主账号Token
    # appId 应用ID
    # clientNumber 子账号ID
    # date 枚举类型 day 代表前一天的数据（从00:00 – 23:59）；week代表前一周的数据(周一 到周日)；month表示上一个月的数据
    def getClientBillList(self, accountSid, accountToken, appId, clientNumber, date, isUseJson=True):
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y%m%d%H%M%S")
        signature = getSig(accountSid, accountToken, timestamp)
        url = self.HOST + ":" + self.PORT + "/" + self.SOFTVER + "/Accounts/" + accountSid + "/Clients/billList?sig=" + signature

        if isUseJson == True:
            body = '{"clientBill":{"appId":"%s","clientNumber":"%s","date":"%s"}}' % (appId, clientNumber, date)
            responseMode = self.JSON
        else:
            body = "<?xml version='1.0' encoding='utf-8'?>\
					<clientBill>\
						<appId>%s</appId>\
						<clientNumber>%s</clientNumber>\
						<date>%s</date>\
					</clientBill>\
					" % (appId, clientNumber, date)
            responseMode = self.XML

        req = urllib2.Request(url)
        return urlOpen(createHttpReq(req, url, accountSid, timestamp, responseMode, body))

    # client充值
    # accountSid 主账号ID
    # accountToken 主账号Token
    # appId 应用ID
    # clientNumber 子账号ID
    # chargeType  0 充值；1 回收。
    # charge 充值的金额
    def chargeClient(self, accountSid, accountToken, appId, clientNumber, chargeType, charge, isUseJson=True):
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y%m%d%H%M%S")
        signature = getSig(accountSid, accountToken, timestamp)
        url = self.HOST + ":" + self.PORT + "/" + self.SOFTVER + "/Accounts/" + accountSid + "/chargeClient?sig=" + signature

        if isUseJson == True:
            body = '{"client":{"appId":"%s","clientNumber":"%s","chargeType":"%s","charge":"%s"}}' % (
            appId, clientNumber, chargeType, charge)
            responseMode = self.JSON
        else:
            body = "<?xml version='1.0' encoding='utf-8'?>\
					<client>\
						<appId>%s</appId>\
						<clientNumber>%s</clientNumber>\
						<chargeType>%s</chargeType>\
						<charge>%s</charge>\
					</client>\
					" % (appId, clientNumber, chargeType, charge)
            responseMode = self.XML

        req = urllib2.Request(url)
        return urlOpen(createHttpReq(req, url, accountSid, timestamp, responseMode, body))

    # 双向回拨
    # accountSid 主账号ID
    # accountToken 主账号Token
    # appId 应用ID
    # fromClient 主叫的clientNumber
    # toNumber 被叫的号码
    # maxallowtime 允许的最大通话时长
    def callBack(self, accountSid, accountToken, appId, fromClient, to, fromSerNum, toSerNum, maxAllowTime,
                 isUseJson=True):
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y%m%d%H%M%S")
        signature = getSig(accountSid, accountToken, timestamp)
        url = self.HOST + "/" + self.SOFTVER + "/Accounts/" + accountSid + "/Calls/callBack?sig=" + signature
        print("url:%s" % url)
        if isUseJson == True:
            body = '{"callback":{ "appId":"%s","fromClient":"%s","to":"%s", "fromSerNum" : "%s","toSerNum"   : "%s"}}' % (
            appId, fromClient, to, fromSerNum, toSerNum, maxAllowTime)
            responseMode = self.JSON
            print(body)
        else:
            body = "<?xml version='1.0' encoding='utf-8'?>\
					<callback>\
						<appId>%s</appId>\
						<fromClient>%s</fromClient>\
						<to>%s</to>\
						<fromSerNum>%s</fromSerNum>\
						<toSerNum>%s</toSerNum>\
						<maxallowtime>%s</maxallowtime>\
					</callback>\
					" % (appId, fromClient, to, fromSerNum, toSerNum, maxAllowTime)
            responseMode = self.XML
            print("body:%s" % body)
        req = urllib2.Request(url)
        return urlOpen(createHttpReq(req, url, accountSid, timestamp, responseMode, body))

    # 语音验证码
    # accountSid 主账号ID
    # accountToken 主账号Token
    # appId 应用ID
    # verifyCode 验证码内容，为数字和英文字母，不区分大小写，长度4-8位
    # toNumber 被叫的号码
    def voiceCode(self, accountSid, accountToken, appId, verifyCode, toNumber, isUseJson=True):
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y%m%d%H%M%S")
        signature = getSig(accountSid, accountToken, timestamp)
        url = self.HOST + ":" + self.PORT + "/" + self.SOFTVER + "/Accounts/" + accountSid + "/Calls/voiceCode?sig=" + signature

        if isUseJson == True:
            body = '{"voiceCode":{ "appId":"%s","verifyCode":"%s","to":"%s"}}' % (appId, verifyCode, toNumber)
            responseMode = self.JSON

        else:
            body = "<?xml version='1.0' encoding='utf-8'?>\
					<voiceCode>\
						<appId>%s</appId>\
						<verifyCode>%s</verifyCode>\
						<to>%s</to>\
					</voiceCode>\
					" % (appId, verifyCode, toNumber)
            responseMode = self.XML

        req = urllib2.Request(url)
        return urlOpen(createHttpReq(req, url, accountSid, timestamp, responseMode, body))

    # 短信验证码（模板短信）
    # accountSid 主账号ID
    # accountToken 主账号Token
    # appId 应用ID
    # toNumber 被叫的号码
    # templateId 模板Id
    # param <可选> 内容数据，用于替换模板中{数字}
    def templateSMS(self, accountSid, accountToken, appId, toNumbers, templateId, param, isUseJson=True):
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y%m%d%H%M%S")
        signature = getSig(accountSid, accountToken, timestamp)
        url = self.HOST + ":" + self.PORT + "/" + self.SOFTVER + "/Accounts/" + accountSid + "/Messages/templateSMS?sig=" + signature

        if isUseJson == True:
            body = '{"templateSMS":{ "appId":"%s","to":"%s","templateId":"%s","param":"%s"}}' % (
            appId, toNumbers, templateId, param)
            responseMode = self.JSON
        else:
            body = "<?xml version='1.0' encoding='utf-8'?>\
					<templateSMS>\
						<appId>%s</appId>\
						<to>%s</to>\
						<templateId>%s</templateId>\
						<param>%s</param>\
					</templateSMS>\
					" % (appId, toNumbers, templateId, param)
            responseMode = self.XML

        req = urllib2.Request(url)
        return urlOpen(createHttpReq(req, url, accountSid, timestamp, responseMode, body))


def main():
    test = RestAPI()

    accountSid = "e03bc9106c6ed0eaebfce8c368fded32"
    accountToken = "477ad4fde64a52390c1edc81cd7bwe32"
    appId = "b73abb6d451346efa13370172d19c7c9"
    to = "13012345678"
    fromClient = "66098000367509"
    fromSerNum = "075512345678"
    toSerNum = "13512345678"
    clientNumber = "66098000367509"

    mobile = "15012345678"
    friendlyName = "test007"
    # 1分钱 = 10000。 charge单位是元
    charge = "8"
    clientType = "1"

    start = "0"
    limit = "100"
    isUseJson = False
    date = "day"
    chargeType = "0"
    maxAllowTime = "60"

    displayNum = "15012345678"
    verifyCode = "1234"
    toNumber = "15012345678"
    templateId = "1"
    param = "3321"


# 查询主账号
# print(test.getAccountInfo(accountSid,accountToken,isUseJson))
# 申请子账号
# print(test.applyClient(accountSid,accountToken,appId,clientType,charge,friendlyName,mobile,isUseJson))
# 查询子账号列表
# print(test.getClientList(accountSid,accountToken,appId,start,limit,isUseJson))
# 删除一个子账号
# print(test.ReleaseClient(accountSid,accountToken,clientNumber,appId,isUseJson))
# 查询子账号信息(clientNumber方式)
# print(test.getClientInfo(accountSid,accountToken,appId,clientNumber,isUseJson))
# 查询子账号信息(mobile方式)
# print(test.getClientInfoByMobile(accountSid,accountToken,appId,mobile,isUseJson))
# 查询应用话单
# print(test.getBillList(accountSid,accountToken,appId,date,isUseJson))
# 子账号充值
# print(test.chargeClient(accountSid,accountToken,appId,clientNumber,chargeType,charge,isUseJson))
# 回拨
# print(test.callBack(accountSid,accountToken,appId,fromClient,to,fromSerNum,toSerNum,maxAllowTime,isUseJson))
# 语音验证码
# print(test.voiceCode(accountSid,accountToken,appId,verifyCode,toNumber,isUseJson))
# 短信
# print(test.templateSMS(accountSid,accountToken,appId,toNumber,templateId,param,isUseJson))

if __name__ == "__main__":
    main()

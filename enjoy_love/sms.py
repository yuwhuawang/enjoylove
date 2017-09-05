#coding:utf-8
from __future__ import unicode_literals

import sys
from enjoylove.mns_python_sdk.mns.account import Account
from django.conf.settings import Endpoint, AccessKeyId, AccessKeySecret, Topic

from enjoylove.mns_python_sdk.mns.topic import DirectSMSInfo, TopicMessage

from enjoylove.mns_python_sdk.mns.mns_exception import MNSExceptionBase


def send_sms_verify_code(mobile, code):

    msg_body1 = "sms-message1."
    my_account = Account(Endpoint, AccessKeyId, AccessKeySecret)
    my_topic = my_account.get_topic(Topic)
    direct_sms_attr1 = DirectSMSInfo(free_sign_name="$YourSignName", template_code="$YourSMSTemplateCode", single=False)
    direct_sms_attr1.add_receiver(receiver=mobile, params={"$YourSMSTemplateParamKey1": code})
    msg1 = TopicMessage(msg_body1, direct_sms=direct_sms_attr1)

    try:
        re_msg = my_topic.publish_message(msg1)
        print "Publish Message Succeed. MessageBody:%s MessageID:%s" % (msg_body1, re_msg.message_id)
    except MNSExceptionBase,e:
        if e.type == "TopicNotExist":
            print "Topic not exist, please create it."
            sys.exit(1)
        print "Publish Message Fail. Exception:%s" % e
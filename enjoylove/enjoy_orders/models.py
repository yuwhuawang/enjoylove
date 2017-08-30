# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import urllib
import uuid

import datetime
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django_extensions.db.models import TimeStampedModel
import time
import json
# Create your models here.
from enjoy_love.models import User
from utils import safe_utf8


NOTIFY_STATUS_READY = 0
NOTIFY_STATUS_SUCCESS = 1
NOTIFY_STATUS_FAILURE = 2

NOTIFY_STATUS_CHOICE = (
    (NOTIFY_STATUS_READY, _("Ready")),
    (NOTIFY_STATUS_SUCCESS, _("Success")),
    (NOTIFY_STATUS_FAILURE, _("Failure")),
)


PARTNERNOTIFY_STATE_READY = 1
PARTNERNOTIFY_STATE_RETRY_1 = 2
PARTNERNOTIFY_STATE_RETRY_2 = 3
PARTNERNOTIFY_STATE_RETRY_3 = 4
PARTNERNOTIFY_STATE_RETRY_4 = 5
PARTNERNOTIFY_STATE_FAILURE = 6
PARTNERNOTIFY_STATE_FINISHED = 7

PARTNERNOTIFY_STATE_CHOICES = (
    (PARTNERNOTIFY_STATE_READY, _("Ready")),
    (PARTNERNOTIFY_STATE_RETRY_1, _("First Retry")),
    (PARTNERNOTIFY_STATE_RETRY_2, _("Second Retry")),
    (PARTNERNOTIFY_STATE_RETRY_3, _("Third Retry")),
    (PARTNERNOTIFY_STATE_RETRY_4, _("4th Retry")),
    (PARTNERNOTIFY_STATE_FAILURE, _("Failure")),
    (PARTNERNOTIFY_STATE_FINISHED, _("Finished")),
)

RECEIPT_STATUS_READY = 1
RECEIPT_STATUS_SUCCEED = 2
RECEIPT_STATUS_FAILURE = 3
RECEIPT_STATUS_CLOSED = 4

RECEIPT_STATUS_CHOICE = (
    (RECEIPT_STATUS_READY, _("Ready")),
    (RECEIPT_STATUS_SUCCEED, _("Succeed")),
    (RECEIPT_STATUS_FAILURE, _("Failure")),
    (RECEIPT_STATUS_CLOSED, _("Closed")),
)

RECEIPT_STATUS_MSG = {
    RECEIPT_STATUS_READY: u'OK',
    RECEIPT_STATUS_SUCCEED: u'订单支付成功',
    RECEIPT_STATUS_FAILURE: u'订单支付失败',
    RECEIPT_STATUS_CLOSED: u'订单已经关闭',
}


RECEIPT_STATE_READY = 1
RECEIPT_STATE_NOTIFY_RECEIVED = 2
RECEIPT_STATE_PARTNER_NOTIFY_PROCESSED = 3
RECEIPT_STATE_FINISHED = 4

RECEIPT_STATE_CHOICES = (
    (RECEIPT_STATE_READY, _("Ready")),
    (RECEIPT_STATE_NOTIFY_RECEIVED, _("Notify received")),
    (RECEIPT_STATE_PARTNER_NOTIFY_PROCESSED, _("Partner notify processed")),
    (RECEIPT_STATE_FINISHED, _("Finished")),
)

NOTIFY_STATE_RECEIVED = 1
NOTIFY_STATE_RECEIPT_PROCESSED = 2
NOTIFY_STATE_FINISHED = 3
NOTIFY_STATE_FAILURE = 4

NOTIFY_STATE_CHOICES = (
    (NOTIFY_STATE_RECEIVED, _("Received")),
    (NOTIFY_STATE_RECEIPT_PROCESSED, _("Receipt processed")),
    (NOTIFY_STATE_FINISHED, _("Finished")),
    (NOTIFY_STATE_FAILURE, _("Failure")),
)


class Orders(models.Model):

    class Meta:
        verbose_name = "订单"
        verbose_name_plural = "订单"
        ordering = ('-purchase_date', '-generate_date', )

    oid = models.CharField("商品id", max_length=64, blank=True)
    product_name = models.CharField("商品名称", max_length=64, blank=True, null=True)
    outer_order_id = models.CharField(_("Outer Order"), max_length=64,
                                      null=True, blank=True)
    outer_trade_no = models.CharField(_("Outer trade no"), max_length=64,
                                      null=True, blank=True)
    user = models.ForeignKey(User)
    good = models.ForeignKey("Goods")
    count = models.IntegerField("数量")
    amount = models.IntegerField("总价(分)")
    platform = models.CharField("来源平台", max_length=64, blank=True, null=True)
    currency = models.CharField("货币", max_length=8, default="CNY")

    status = models.IntegerField(_("Status"), choices=RECEIPT_STATUS_CHOICE,
                                 default=RECEIPT_STATUS_READY)
    generate_date = models.DateTimeField(_("Generated Date"),
                                         auto_now_add=True)
    purchase_date = models.DateTimeField(_("Purchased Date"),
                                         null=True, blank=True)
    pay_type = models.CharField(_("Pay Type"), max_length=32, default='',
                                blank=True)
    notify_url = models.CharField(_("Notify URL"), max_length=256, blank=True)
    state = models.IntegerField(_("State"), choices=RECEIPT_STATE_CHOICES,
                                default=RECEIPT_STATE_READY)

    def __unicode__(self):
        return unicode(self.oid)

    def __str__(self):
        return str(self.oid)

    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = str(uuid.uuid4()).replace('-', '')
        super(Orders, self).save(*args, **kwargs)


class Goods(models.Model):
    class Meta:
        verbose_name = "商品"
        verbose_name_plural = "商品"
    gid = models.CharField("商品id", max_length=64, blank=True)
    name = models.CharField(max_length=20)
    desc = models.TextField()
    price = models.DecimalField(decimal_places=2, max_digits=15)
    currency = models.CharField("货币", max_length=8)
    discount = models.DecimalField("折扣", decimal_places=2, max_digits=15,
                                   default=0.0)
    price_actual = models.DecimalField(decimal_places=2, max_digits=15)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = str(uuid.uuid4()).replace('-', '')

        if "discount" in kwargs and "price_actual" in kwargs:
            self.discount = self.price_actual / self.price

        if "discount" in kwargs:
            self.price_actual = self.price * self.discount

        if "price_actual" in kwargs:
            self.discount = self.price_actual / self.price
        super(Goods, self).save(*args, **kwargs)


class WeixinToken(TimeStampedModel):

    token = models.CharField(_("Token"), max_length=256)
    expires_in = models.DateTimeField(_("Expires in"))

    class Meta:
        verbose_name = _("Weixin Token")
        verbose_name_plural = _("Weixin Tokens")
        ordering = ('-modified', )

    def __unicode__(self):
        return unicode(self.token)


class Notify(models.Model):

    uuid = models.CharField(_("Notify ID"), max_length=64, unique=True)
    order_sn = models.CharField(_("Order SN"), max_length=64)
    outer_order_sn = models.CharField(_("Outer Order SN"), max_length=64,
                                      null=True, blank=True)
    status = models.CharField(_("Status"), max_length=16)
    state = models.IntegerField(_("State"), choices=NOTIFY_STATE_CHOICES,
                                default=NOTIFY_STATE_RECEIVED)
    source = models.CharField(_("Source"), max_length=32)
    retry = models.IntegerField(_("Retry"), default=0)
    trade_date = models.DateTimeField(_("Trade Date"))
    create_date = models.DateTimeField(_("Created at"), auto_now_add=True)

    class Meta:
        ordering = ("-create_date", )


class CallbackNotify(models.Model):

    uuid = models.CharField(_("UUID"), max_length=64,
                            default=lambda: uuid.uuid4().get_hex())
    callback_url = models.CharField(_("Callback URL"), max_length=256)
    product_name = models.CharField(_("Product Name"), max_length=64)
    amount = models.IntegerField(_("Amount"))
    currency = models.CharField(_("Currency"), max_length=8)
    trans_no = models.CharField(_("Receipt UUID"), max_length=64)
    result = models.CharField(_("Result"), max_length=8)
    trade_time = models.BigIntegerField(_("Trade time"))

    status = models.IntegerField(_("Status"), choices=NOTIFY_STATUS_CHOICE,
                                 default=NOTIFY_STATUS_READY)
    sign = models.CharField(_("Signature"), max_length=1024)
    sign_type = models.CharField(_("Sign type"), max_length=8)
    resp = models.TextField(_("Response"), blank=True, null=True)
    state = models.IntegerField(_("State"), default=PARTNERNOTIFY_STATE_READY,
                                choices=PARTNERNOTIFY_STATE_CHOICES)
    send_time = models.DateTimeField(_("Should send after at"))
    create_date = models.DateTimeField(_("Created at"), auto_now_add=True)

    class Meta:
        ordering = ('-create_date', )

    def __unicode__(self):
        return unicode(self.uuid)

    @classmethod
    def fromReceipt(cls, receipt):
        trade_time = receipt.purchase_date or datetime.now()
        trade_time = int(time.mktime(trade_time.timetuple()))

        try:
            extra = json.loads(receipt.extra)
        except:
            extra = {}
        product_id = extra.get('product_id')

        sign_data = dict(
            notify_id=uuid.uuid4().get_hex(),
            product=product_id,
            extra=receipt.appendAttr,
            trans_no=receipt.uuid,
            result=receipt.get_trade_result(),
            trade_time=trade_time,
            amount=receipt.amount,
            currency=receipt.currency)
        sign_data['sign'] = receipt.client.sign_dict(sign_data)
        sign_data['sign_type'] = 'rsa'
        sign_data['uuid'] = sign_data['notify_id']
        del sign_data['notify_id']
        sign_data['product_name'] = sign_data['product']
        del sign_data['product']
        sign_data['send_time'] = datetime.now()
        sign_data['callback_url'] = receipt.notify_url
        sign_data['client'] = receipt.client

        return cls.objects.create(**sign_data)

    def dumpMessage(self):
        data = dict(
            product=self.product_name,
            extra=self.extra,
            trans_no=self.trans_no,
            result=self.result,
            notify_id=self.uuid,
            trade_time=self.trade_time,
            amount=self.amount,
            currency=self.currency,
            sign=self.sign,
            sign_type=self.sign_type)
        for k, v in data.items():
            data[k] = safe_utf8(v)
        return urllib.urlencode(data)





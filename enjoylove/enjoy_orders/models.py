# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django_extensions.db.models import TimeStampedModel

# Create your models here.
from enjoy_love.models import User



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

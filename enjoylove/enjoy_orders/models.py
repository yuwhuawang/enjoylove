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


class Orders(models.Model):

    class Meta:
        verbose_name = "订单"
        verbose_name_plural = "订单"
        ordering = ('-modified', '-created', )

    oid = models.CharField("商品id", max_length=64, blank=True)
    outer_order_id = models.CharField(_("Outer Order"), max_length=64,
                                      null=True, blank=True)
    outer_trade_no = models.CharField(_("Outer trade no"), max_length=64,
                                      null=True, blank=True)
    user = models.ForeignKey(User)
    good = models.ForeignKey("Goods")
    platform = models.CharField("来源平台", blank=True, null=True)
    currency = models.CharField("货币", max_length=8)

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
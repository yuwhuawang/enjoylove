# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid

from django.db import models

# Create your models here.
from enjoy_love.models import User


class Orders(models.Model):

    class Meta:
        verbose_name = "订单"
        verbose_name_plural = "订单"

    order_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User)
    good = models.ForeignKey("Goods")
    status = models.SmallIntegerField("状态", default=0)
    pay_id = models.CharField("支付id", max_length=25, null=True, blank=True)


class Goods(models.Model):
    class Meta:
        verbose_name = "商品"
        verbose_name_plural = "商品"

    name = models.CharField(max_length = 20)
    desc = models.TextField()
    price = models.DecimalField(decimal_places=2, max_digits= 15)

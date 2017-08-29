#coding:utf-8
__author__ = 'yuwhuawang'
__created__ = '2017/08/29 23:24'


import celery
import datetime
import logging

from django.db import transaction

from lock import RedisLock as Lock
from utils import httputil
from models import Notify, Orders
import models

@celery.task
def processNotify(uuid):
    from tasks import processReceipt

    nlock = Lock('notify:{}'.format(uuid))
    if nlock.acquire():
        try:
            try:
                notify = Notify.objects.get(uuid=uuid)
            except Notify.DoesNotExist:
                return False, 'Notify {} not exists'.format(uuid)

            if notify.state in [models.NOTIFY_STATE_FINISHED,
                                models.NOTIFY_STATE_FAILURE]:
                return True, 'Notify {} already processed'.format(uuid)

            with transaction.atomic():
                if notify.state == models.NOTIFY_STATE_RECEIPT_PROCESSED:
                    notify.state = models.NOTIFY_STATE_FINISHED
                    notify.save()
                    return True, 'Notify {} is proccessed'.format(notify.uuid)
                if not notify.status:
                    notify.state = models.NOTIFY_STATE_FINISHED
                    notify.save()
                    return True, 'Notify {} not succeed, skipped'.format(uuid)
                try:
                    receipt = Orders.objects.get(uuid=notify.order_sn)
                except Orders.Receipt.DoesNotExist:
                    notify.state = models.NOTIFY_STATE_FAILURE
                    notify.save()
                    return False, 'Receipt {} not exists'.format(
                        notify.order_sn)

                if receipt.state in [models.RECEIPT_STATE_READY, ]:
                    rlock = Lock('receipt:{}'.format(receipt.uuid))
                    if rlock.acquire():
                        try:
                            receipt.onNotify(notify)
                            notify.state = \
                                models.NOTIFY_STATE_RECEIPT_PROCESSED
                            notify.save()
                        finally:
                            rlock.release()
                else:
                    notify.state = models.NOTIFY_STATE_FINISHED
                    notify.save()
                    return True, 'Receipt {} already processed'.format(
                        receipt.uuid)
            processReceipt.delay(receipt.uuid)
            return True, 'Receipt {} is proccessed'.format(receipt.uuid)
        finally:
            nlock.release()
    else:
        return False, 'Notify {} processed by other worker'.format(uuid)
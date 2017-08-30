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



@celery.task
def processReceipt(uuid):
    #from notify import models as nmodels
    #from notify import tasks as ntasks

    rlock = Lock('receipt:{}'.format(uuid))
    if rlock.acquire():
        try:
            try:
                receipt = Orders.objects.get(uuid=uuid)
            except Orders.DoesNotExist:
                return False, 'Receipt {} not exists'.format(uuid)

            if receipt.state in [models.RECEIPT_STATE_FINISHED, ]:
                return True, 'Receipt {} already processed'.format(uuid)
            elif receipt.state in [models.RECEIPT_STATE_READY, ]:
                return False, 'Receipt {} is not ready'.format(uuid)
            else:
                # RECEIPT_STATE_NOTIFY_RECEIVED
                with transaction.atomic():
                    if receipt.state == \
                            models.RECEIPT_STATE_PARTNER_NOTIFY_PROCESSED:
                        receipt.state = models.RECEIPT_STATE_FINISHED
                        receipt.save()
                        return True, 'Receipt {} finished'.format(uuid)
                    if not receipt.notify_url:
                        receipt.state = models.RECEIPT_STATE_FINISHED
                        receipt.save()
                        return True, 'Receipt {} finished'.format(uuid)
                    else:
                        receipt.state = \
                            models.RECEIPT_STATE_PARTNER_NOTIFY_PROCESSED
                        receipt.save()
                        notify = models.CallbackNotify.fromReceipt(receipt)

                processCallbackNotify.delay(notify)
                return True, 'Process {} processed'.format(uuid)
        finally:
            rlock.release()
    else:
        return False, 'Receipt {} processed by other worker'.format(uuid)


@celery.task
def processCallbackNotify(uuid):
    try:
        notify = nmodels.CallbackNotify.objects.get(uuid=uuid)
    except nmodels.CallbackNotify.DoesNotExist:
        return False, 'CallbackNotify {} not found'.format(uuid)

    if notify.state == nmodels.PARTNERNOTIFY_STATE_FINISHED:
        return True, 'Callback Notify {} already processed'.format(uuid)
    if notify.state == nmodels.PARTNERNOTIFY_STATE_FAILURE:
        return False, 'Callback Notify {} too many failure'.format(uuid)
    if notify.send_time > datetime.datetime.now():
        return False, 'Callback Notify {} not ready for process'.format(uuid)

    lock = Lock('cn:{}'.format(uuid))
    if lock.acquire():
        try:
            message = notify.dumpMessage()
            resp = httputil.get(notify.callback_url, message)
            with transaction.atomic():
                notify.resp = resp
                if resp == 'success':
                    notify.status = nmodels.NOTIFY_STATUS_SUCCESS
                    notify.state = nmodels.PARTNERNOTIFY_STATE_FINISHED
                    notify.save()
                    return True, 'Callback notify {} succeed'.format(uuid)
                else:
                    if notify.state not in [
                            nmodels.PARTNERNOTIFY_STATE_RETRY_4, ]:
                        notify.state = notify.state + 1
                        notify.send_time = notify.send_time + \
                            datetime.timedelta(seconds=60)
                    else:
                        notify.state = nmodels.PARTNERNOTIFY_STATE_FAILURE
                    notify.status = nmodels.NOTIFY_STATUS_FAILURE
                    notify.save()

                    if notify.state == nmodels.PARTNERNOTIFY_STATE_FAILURE:
                        processCallbackFailure.delay(notify)

                    return False, 'Callback notify {} failure'.format(uuid)
        finally:
            lock.release()
    else:
        return False, 'Can not acquire lock {}'.format(lock.key)
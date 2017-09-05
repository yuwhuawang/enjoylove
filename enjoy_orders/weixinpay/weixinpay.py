# coding:utf-8
from rest_framework.exceptions import APIException
from .import weixinpay_config
from .import weixinpay_core
from ..utils import get_client_ip



def make_payment_info(request=None, notify_url=None, out_trade_no=None, total_fee=None):
    order_info = {'appid': weixinpay_config.APP_ID,
                  'mch_id': weixinpay_config.MCH_ID,
                  'device_info': 'WEB',
                  'nonce_str': '',
                  'sign_type': weixinpay_config.SIGN_TYPE,
                  'body': weixinpay_config.BODY,
                  'out_trade_no': str(out_trade_no),
                  'total_fee': total_fee,
                  'spbill_create_ip': get_client_ip(request),
                  'notify_url': notify_url,
                  'trade_type': 'APP'}
    return order_info


def make_payment_request_wx(request, out_trade_no, total_fee):
    """
    微信统一下单，并返回客户端数据
    :param notify_url: 回调地址
    :param out_trade_no: 订单编号
    :param total_fee: 充值金额
    :return: app所需结果数据
    """
    if float(total_fee) < 0.01:
        raise APIException('充值金额不能小于0.01')
    payment_info = make_payment_info(request, notify_url=weixinpay_config.NOTIFY_URL, out_trade_no=out_trade_no, total_fee=total_fee)
    res = weixinpay_core.make_payment_request(payment_info)
    return res


def weixinpay_call_back(request):
    """
    微信支付回调
    :param request: 回调参数
    :return:
    """
    args = request.body
    # 验证平台签名
    resp_dict = weixinpay_core.handle_wx_response_xml(args)
    if resp_dict is None:
        return
    return resp_dict


def weixinpay_response_xml(params):
    """
    生成交易成功返回信息
    """
    return_info = {
        'return_code': params,
        'return_msg': 'OK'
    }
    return weixinpay_core.generate_response_data(return_info)


class WeixinNotifyUtil(WeixinBaseUtil):

    def __init__(self, notify_data, source='weixin'):
        self.notify_data = notify_data
        self.source = source

    def isValid(self):
        data = self.notify_data
        return self.verify(data, data['sign'],
                           [k for k in data if k != 'sign'])

    def getTradeInfo(self):
        data = self.notify_data

        obj = {}
        obj['source'] = self.source
        obj['uuid'] = uuid.uuid4().get_hex()
        obj['order_sn'] = data['out_trade_no']
        obj['outer_order_sn'] = data['transaction_id']
        obj['trade_date'] = datetime.datetime.strptime(data['time_end'],
                                                       '%Y%m%d%H%M%S')
        obj['status'] = data['return_code'] == 'SUCCESS' and \
            data['result_code'] == 'SUCCESS'

        return obj

    def getSuccessMessage(self):
        return XmlUtil.dict_to_xml({'return_code': 'SUCCESS'})

    def getErrorMessage(self):
        return XmlUtil.dict_to_xml({'return_code': 'FAILURE'})
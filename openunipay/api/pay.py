#coding:utf-8
from rest_framework.views import APIView

from openunipay.models import Product

from enjoy_love.api_result import BusinessError

from enjoy_love.api_result import ApiResult

__author__ = 'yuwhuawang'
__created__ = '2017/08/30 22:23'

from openunipay.paygateway import unipay
from openunipay.models import PAY_WAY_WEIXIN,PAY_WAY_ALI
from openunipay.util.client_ip import get_client_ip


class CreateOrderView(APIView):

    def post(self, request):

        client_ip = get_client_ip(request)
        product_id = request.POST.get("product_id")
        pay_type = request.POST.get("pay_type")
        uid = request.POST.get("uid")

        try:
            product = Product.objects.get(pk=product_id)
            res = unipay.create_order(pay_type, client_ip, product.product_desc, product.product_detail, product.fee, uid)
            return ApiResult(result=res)

        except Product.DoesNotExist:
            return BusinessError(u"商品不存在")



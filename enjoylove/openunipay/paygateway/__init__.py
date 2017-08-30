class PayGateway(object):
    '''
    @summary: the base class for pay gateway
    '''

    def create_order(self, orderItemObj, clientIp, **kwargs):
        pass

    def query_order(self, orderNo):
        '''
        @summary: query pay result of order
        @return: PayResult
        '''
        pass

    def process_notify(self, requestContent):
        '''
        @summary: process notify from pay interface
        @return: PayResult
        '''
        pass

    def generate_qr_pay_url(self, productid):
        '''
        @summary: create url that can be used to generate qr code
        @return: url
        '''
        pass

    def process_qr_pay_notify(self, requestContent):
        '''
        @summary: process qr notify
        @return: proudct id,uid
        '''
        pass


class PayResult(object):
    def __init__(self, orderNo, succ=True, lapsed=False):
        self.orderno = orderNo
        self.succ = succ
        self.lapsed = lapsed

    @property
    def OrderNo(self):
        '''
        @summary: order No or merchant
        '''
        return self.orderno

    @property
    def Succ(self):
        '''
        @summary: True: paid successfully
        '''
        return self.succ

    @property
    def Lapsed(self):
        '''
        @summary: True: order is lapsed
        '''
        return self.lapsed

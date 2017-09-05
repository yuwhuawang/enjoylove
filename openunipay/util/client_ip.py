#coding:utf-8
__author__ = 'yuwhuawang'
__created__ = '2017/08/30 22:36'


def get_client_ip(request):
    if 'HTTP_X_REAL_IP' in request.META:
        ip = request.META['HTTP_X_REAL_IP']
    elif 'HTTP_X_FORWARDED_FOR' in request.META:
        ip = request.META['HTTP_X_FORWARDED_FOR'].split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip.strip() or ''
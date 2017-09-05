#coding=utf-8
"""
Django settings for enjoylove project.

Generated by 'django-admin startproject' using Django 1.11.3.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
#SECRET_KEY = '^d=vs@k+o$=y3dn%k)f2+k*7t%xx5u4swnacsfts5lizfkwqrz'
SECRET_KEY = 'lalaneo'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

# Application definition

INSTALLED_APPS = [
    'grappelli',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'gunicorn',
    'enjoy_love',
    'enjoy_post',
    #'enjoy_orders',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_swagger',
    'rest_framework_docs',
    'dueditor',
    'openunipay',
    'import_export'


]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'enjoylove.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

            ],
        },
    },
]

WSGI_APPLICATION = 'enjoylove.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases


DB_NAME = 'enjoylove'
DB_USERNAME = 'yuwhuawang'
DB_PASSWORD = 'wyhwyh22'
#DB_HOST = '123.206.174.249'
DB_HOST = '127.0.0.1'
DB_PORT = '3306'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': DB_NAME,
        'USER': DB_USERNAME,
        'PASSWORD': DB_PASSWORD,
        'HOST': DB_HOST,
        'PORT': DB_PORT,
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'zh-CN'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join("/data/static/")

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

JWT_AUTH = {
    'JWT_ENCODE_HANDLER':
        'rest_framework_jwt.utils.jwt_encode_handler',

    'JWT_DECODE_HANDLER':
        'rest_framework_jwt.utils.jwt_decode_handler',

    'JWT_PAYLOAD_HANDLER':
        'rest_framework_jwt.utils.jwt_payload_handler',

    'JWT_PAYLOAD_GET_USER_ID_HANDLER':
        'rest_framework_jwt.utils.jwt_get_user_id_from_payload_handler',

    'JWT_RESPONSE_PAYLOAD_HANDLER':
        'rest_framework_jwt.utils.jwt_response_payload_handler',

    'JWT_GET_USER_SECRET_KEY': None,
    'JWT_PUBLIC_KEY': None,
    'JWT_PRIVATE_KEY': None,
    'JWT_ALGORITHM': 'HS256',
    'JWT_VERIFY': True,
    'JWT_VERIFY_EXPIRATION': False,
    'JWT_LEEWAY': 0,
    'JWT_AUDIENCE': None,
    'JWT_ISSUER': None,

    'JWT_ALLOW_REFRESH': False,
    'JWT_REFRESH_EXPIRATION_DELTA': datetime.timedelta(days=7),

    'JWT_AUTH_HEADER_PREFIX': 'JWT',
    'JWT_AUTH_COOKIE': None,

}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },  # 针对 DEBUG = True 的情况
    },
    'formatters': {
        'standard': {
            'format': '%(levelname)s %(asctime)s %(pathname)s %(filename)s %(module)s %(funcName)s %(lineno)d: %(message)s'
        },  # 对日志信息进行格式化，每个字段对应了日志格式中的一个字段，更多字段参考官网文档，我认为这些字段比较合适，输出类似于下面的内容
        # INFO 2016-09-03 16:25:20,067 /home/ubuntu/mysite/views.py views.py views get 29: some info...
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'standard'
        },
        'file_handler': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(BASE_DIR, "logs/enjoy.log"),
            'formatter': 'standard'
        },  # 用于文件输出
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file_handler', 'console'],
            'level': 'DEBUG',
            'propagate': True  # 是否继承父类的log信息
        },  # handlers 来自于上面的 handlers 定义的内容
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
    }
}

# aliyun sms
AccessKeyId = "LTAI9H13RjIiNvm2"
AccessKeySecret = "SVFEpV0mOsJqPEMPMCNSBVRUuz60XP"
Endpoint = "https://1725191364816734.mns.cn-hangzhou.aliyuncs.com/"
Topic = "sms.topic-cn-hangzhou"

# ucpaas sms
SMS_APPID = "9e5762cfb871469d86e129f97aa9c7b1"
SMS_ACCOUNTSID = "70188edf2e490428560987a55ce7b0c3"
SMS_AUTHTOKEN = "cf80517de55175342754598abdbb1119"
SMS_APIURL = 'https://api.ucpaas.com'
SMS_VERSION = '2014-06-30'
SMS_TEMPLATE_ID = '105543'
SMS_FUNCTION = "Messages"
SMS_OPERATION = "templateSMS"

#ATOMIC_REQUESTS = True


#AUTH_USER_MODEL = 'enjoy_love.User'

GRAPPELLI_ADMIN_TITLE = "enjoylove"
GRAPPELLI_SWITCH_USER = True


#####支付宝支付配置
ALIPAY = {
'partner':'XXX',  #支付宝partner ID
'seller_id':'XXX', #收款方支付宝账号如 pan.weifeng@live.cn
'notify_url':'https:#XXX/notify/alipay/', #支付宝异步通知接收URL
'ali_public_key_pem':'PATH to PEM File', #支付宝公钥的PEM文件路径,在支付宝合作伙伴密钥管理中查看(需要使用合作伙伴支付宝公钥)。如何查看，请参看支付宝文档
'rsa_private_key_pem':'PATH to PEM File',#您自己的支付宝账户的私钥的PEM文件路径。如何设置，请参看支付宝文档
'rsa_public_key_pem':'PATH to PEM File',#您自己的支付宝账户的公钥的PEM文件路径。如何设置，请参看支付宝文档
}
#####微信支付配置
WEIXIN = {
'app_id':'XXX', #微信APPID
'app_seckey':'XXX', #微信APP Sec Key
'mch_id':'XXX', #微信商户ID
'mch_seckey':'XXX',#微信商户seckey
'mch_notify_url':'https://XXX/notify/weixin/', #微信支付异步通知接收URL
'clientIp':'',#扫码支付时，会使用这个IP地址发送给微信API, 请设置为您服务器的IP
}


#七牛配置
QINIU = {
    "access_key": "rPYAMUiFJfHPzG3meWILMARcIu-djqhv51a2lMO4",
    "secret_key": "vGGTStOr2uuQR0CmKff3D3h6dfWT8V77uGMeOCMD",
    "default_bucket": "xianglian-sns"
}
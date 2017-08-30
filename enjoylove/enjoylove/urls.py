"""enjoylove URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
import rest_framework_jwt.views
from django.conf.urls import url, include
from django.contrib import admin
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework_swagger.views import get_swagger_view
from enjoy_love.views import user_init


schema_view = get_swagger_view(title='Pastebin API')


urlpatterns = [
    url(r'^grappelli/', include('grappelli.urls')), # grappelli URLS
    url(r'^admin/', include(admin.site.urls)), # admin site
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^user/', include('enjoy_love.urls')),
    url(r'^init', user_init),
    url(r'^api-token-auth/', obtain_jwt_token),
    url(r'^api/$', schema_view),
    url(r'^docs/', include('rest_framework_docs.urls')),
    url(r'^pay/', include('openunipay.api.urls'))

]

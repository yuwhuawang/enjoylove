#coding:utf-8
from django.conf.urls import include, url
from views import ( CreatePostView, )
urlpatterns = [
    url(r'^create', CreatePostView.as_view()),
]
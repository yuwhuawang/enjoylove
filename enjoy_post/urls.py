#coding:utf-8
from django.conf.urls import include, url
from views import (CreatePostView, SetPostLikeView)
urlpatterns = [
    url(r'^create', CreatePostView.as_view()),
    url(r'^like', SetPostLikeView.as_view()),
]
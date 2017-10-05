from django.conf.urls import url
from gtest import views
from gtest import tasks

urlpatterns = [
    url(r'^$', views.index),
]

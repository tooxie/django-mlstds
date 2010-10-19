# -*- coding: utf-8 -*-
from .views import fetchmail

from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^fetch/$', fetchmail, name='ml_fetch'),
)

# -*- coding: utf-8 -*-
from ml import urls as ml_urls

from django.conf.urls.defaults import *
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^mail/', include(ml_urls)),
    url(r'^admin/', include(admin.site.urls)),
)

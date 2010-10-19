# -*- coding: utf-8 -*-
from os import path

from django.template.defaultfilters import slugify


def get_app_name():
    return path.basename(path.dirname(path.abspath(__file__)))


def get_subscription_upload_to(instance, filename):
    socket = "%s@%s.%i" % (instance.user, instance.host, instance.port)
    return path.join(get_app_name(), 'ssl', slugify(socket))

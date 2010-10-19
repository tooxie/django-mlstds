# -*- coding: utf-8 -*-
from django.conf import settings


def urls(request):
    url_dict = {}
    for attr in dir(settings):
        if attr.endswith('_URL'):
            url_dict[attr] = getattr(settings, attr).replace('%s', '')
    return url_dict


def language(request):
    try:
        lang = settings.LANGUAGE_CODE[:settings.LANGUAGE_CODE.index('-')]
    except:
        lang = settings.LANGUAGE_CODE
    return {'LANGUAGE': lang}


def site(request):
    from django.contrib.sites.models import Site

    return {'site': Site.objects.get_current()}

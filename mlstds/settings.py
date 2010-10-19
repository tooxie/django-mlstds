# -*- coding: utf-8 -*-
from os.path import abspath, basename, dirname, join
import sys

PROJECT_ABSOLUTE_DIR = dirname(abspath(__file__))
PROJECT_NAME = basename(PROJECT_ABSOLUTE_DIR)
APPS_DIR = join(PROJECT_ABSOLUTE_DIR, "apps")
if APPS_DIR not in sys.path:
    sys.path.insert(0, APPS_DIR)

DEBUG = False
TEMPLATE_DEBUG = DEBUG

TIME_ZONE = 'America/Montevideo'
LANGUAGE_CODE = 'es-uy'
USE_I18N = False
USE_L10N = True

SITE_ID = 1

MEDIA_ROOT = PROJECT_ABSOLUTE_DIR + '/media/'
MEDIA_URL = '/media/'
ADMIN_MEDIA_PREFIX = '/media/admin/'

CSS_URL = '%scss/' % MEDIA_URL
IMG_URL = '%simg/' % MEDIA_URL
JS_URL = '%sjs/' % MEDIA_URL

SECRET_KEY = 'l8s1uh5@vikh6=m=_+d8#rneq6_@)4uhys8yh1it_a3ler0+7$'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    # PROJECT_NAME + '.context_processors.urls',
)

ROOT_URLCONF = PROJECT_NAME + '.urls'

TEMPLATE_DIRS = (
    PROJECT_ABSOLUTE_DIR + '/templates/',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    'ml',
)

try:
    from local_settings import *
except ImportError:
    debug_msg = "Can't find local_settings.py, using default settings."
    try:
        from mod_python import apache
        apache.log_error("%s" % debug_msg, apache.APLOG_NOTICE)
    except ImportError:
        import sys
        sys.stderr.write("%s\n" % debug_msg)

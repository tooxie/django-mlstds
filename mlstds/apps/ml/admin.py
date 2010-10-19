# -*- coding: utf-8 -*-
from .models import (Header, MailingList, Message, MessageHeader, Person,
    Subscription, Thread,)

from django.contrib.admin import site, ModelAdmin


site.register(Header)
site.register(MailingList)
site.register(Message)
site.register(MessageHeader)
site.register(Person)
site.register(Subscription)
site.register(Thread)

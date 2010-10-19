# -*- coding: utf-8 -*-
from django.contrib.sites.models import Site
from django.db.models import (BooleanField, CharField, DateTimeField,
    EmailField, FileField, ForeignKey, ManyToManyField, Model,
    PositiveIntegerField, SlugField, TextField, URLField,)
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify


class Person(Model):
    """
    A person, possibly a member of a mailing list.
    """
    name = CharField(max_length=255, blank=True, null=True)
    email = EmailField(unique=True)
    same_as = ForeignKey('Person', blank=True, null=True)

    def __unicode__(self):
        if self.name:
            return "%s <%s>" % (self.name, self.email)
        else:
            return self.email

    class Meta:
        ordering = ['email', 'name']
        verbose_name = _(u'Person')
        verbose_name_plural = _(u'Persons')


class Subscription(Model):
    """
    A subscription to download a mailing list's messages.
    """
    from .choices import IMAP, POP3, SUBSCRIPTION_PROTOCOL_CHOICES
    from .mailclient import fetchmail
    from .utils import get_subscription_upload_to

    protocol = CharField(max_length=4, choices=SUBSCRIPTION_PROTOCOL_CHOICES)
    user = CharField(max_length=255)
    password = CharField(max_length=255)
    host = CharField(max_length=255)
    port = PositiveIntegerField(blank=True, null=True)
    use_ssl = BooleanField()
    ssl_keyfile = FileField(upload_to=get_subscription_upload_to, blank=True,
        null=True)
    ssl_certfile = FileField(upload_to=get_subscription_upload_to, blank=True,
        null=True)
    mailboxes = CharField(max_length=255, blank=True, null=True)
    last_fetched = PositiveIntegerField(blank=True, null=True)
    disabled = BooleanField()

    def save(self, *args, **kwargs):
        if not self.port:
            if self.protocol == self.IMAP:
                self.port = 143
                if self.use_ssl:
                    self.port = 993
            elif self.protocol == self.POP3:
                self.port = 110
                if self.use_ssl:
                    self.port = 995
        super(Subscription, self).save(*args, **kwargs)

    def get_socket(self):
        socket = self.user
        if '@' in self.user:
            socket = '"%s"' % self.user
        socket += '@%s' % self.host
        if self.port:
            return socket + ':%i' % self.port
        else:
            return socket

    def get_mails(self):
        return self.fetchmail()

    def __unicode__(self):
        return self.get_socket()

    class Meta:
        ordering = ['host', 'port', 'user']
        unique_together = ('user', 'host', 'port')
        verbose_name = _(u'Subscription')
        verbose_name_plural = _(u'Subscriptions')


class MailingList(Model):
    """
    A mailing list.
    """
    from .choices import MAILINGLIST_CHOICES

    name = CharField(max_length=255, blank=True, null=True)
    url = URLField(blank=True, null=True)
    list_id = CharField(max_length=255, unique=True)
    list_post = CharField(max_length=255)
    list_help = CharField(max_length=255)
    list_archive = URLField()
    list_unsubscribe = CharField(max_length=255)
    date_created = DateTimeField(auto_now_add=True)
    site = ForeignKey(Site)
    list_type = CharField(max_length=25, choices=MAILINGLIST_CHOICES,
        blank=True, null=True)
    subscription = ForeignKey(Subscription, related_name='mailing_lists',
        blank=True, null=True)
    members = ManyToManyField(Person)

    def __unicode__(self):
        return self.list_id

    class Meta:
        get_latest_by = 'date_created'
        ordering = ['name', 'url']
        verbose_name = _(u'Mailing list')
        verbose_name_plural = _(u'Mailing lists')


class Message(Model):
    """
    A message sent by a list member.
    """
    message_id = CharField(max_length=255, unique=True)
    # thread = ForeignKey(Thread)
    subject = CharField(max_length=255)
    author = ForeignKey(Person)
    text = TextField()
    date_sent = DateTimeField()
    date_received = DateTimeField(auto_now_add=True)
    in_reply_to = ForeignKey('Message', related_name='responses', blank=True,
        null=True)

    @property
    def is_reply(self):
        return bool(self.in_reply_to)

    @property
    def was_replied(self):
        return bool(Message.objects.filter(in_reply_to=self).count())

    def get_first_in_thread(self):
        if self.in_reply_to:
            return self.in_reply_to.get_first_in_thread()
        else:
            return self

    def get_thread(self):
            return Thread.objects.get(
                first_message=self.get_first_in_thread())

    def get_childs(self):
        return Message.objects.filter(in_reply_to=self)

    def __unicode__(self):
        return self.subject

    class Meta:
        get_latest_by = 'date_sent'
        order_with_respect_to = ''
        ordering = ['date_sent', ]
        verbose_name = _(u'Message')
        verbose_name_plural = _(u'Messages')


class Thread(Model):
    """
    A thread, a sequence of messages.
    """
    subject = CharField(max_length=255)
    first_message = ForeignKey(Message)
    date_last_message = DateTimeField()
    messages_count = PositiveIntegerField(default=1)
    mailing_list = ForeignKey(MailingList, blank=True, null=True)

    def save(self, *args, **kwargs):
        self.messages_count = self._messages_count()
        super(Thread, self).save(*args, **kwargs)

    def _messages_count(self, message=None, count=0):
        count += 1
        if not message:
            message = self.first_message
        for child in message.get_childs():
            count = self._messages_count(child, count)
        return count

    def __unicode__(self):
        return self.subject

    class Meta:
        get_latest_by = 'last_message_date'
        ordering = ['subject', ]
        verbose_name = _(u'Thread')
        verbose_name_plural = _(u'Threads')


class Header(Model):
    """
    A generic header.
    """
    name = CharField(max_length=255, unique=True)
    slug = SlugField()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Header, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name', ]
        verbose_name = _(u'Header')
        verbose_name_plural = _(u'Headers')


class MessageHeader(Model):
    """
    A specific header of a message.
    """
    header = ForeignKey(Header, related_name='headers')
    message = ForeignKey(Message, related_name='headers')
    value = TextField()

    def __unicode__(self):
        return "%s: %s" % (self.header, self.value)

    class Meta:
        order_with_respect_to = 'message'
        ordering = ['header', ]
        # unique_together = ('header', 'message', 'value')
        verbose_name = _(u'Message header')
        verbose_name_plural = _(u'Message headers')

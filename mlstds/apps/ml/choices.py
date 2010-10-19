# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

POP3 = 'POP3'
IMAP = 'IMAP'
SUBSCRIPTION_PROTOCOL_CHOICES = (
    (POP3, 'POP3'),
    (IMAP, 'IMAP'),
)

GOOGLE_GROUPS = 'GOOGLEGROUPS'
YAHOO_GROUPS = 'YAHOOGROUPS'
MAILMAN = 'MAILMAN'
MAILINGLIST_OTHER = None
MAILINGLIST_CHOICES = (
    (GOOGLE_GROUPS, _(u'Google Groups')),
    (YAHOO_GROUPS, _(u'Yahoo Groups')),
    (MAILMAN, _(u'Mailman')),
    (MAILINGLIST_OTHER, _(u'Other')),
)

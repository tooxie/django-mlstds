# -*- coding: utf-8 -*-
from .models import (Header, MailingList, Message, MessageHeader, Person,
    Subscription, Thread,)

from django.contrib.sites.models import Site
from django.http import HttpResponse
from django.template.defaultfilters import slugify

from dateutil.parser import parser

from email.header import decode_header
from email.utils import parseaddr
import re
import unicodedata


def fetchmail(request):
    for subscription in Subscription.objects.exclude(disabled=True):
        last_fetched, mails = subscription.get_mails()
        parse_mails(mails, subscription)
        subscription.last_fetched = last_fetched
        subscription.save()
    print '*** OK'
    return HttpResponse('OK')


def parse_mails(mails, subscription):
    for mail in mails:
        list_id = get_header('List-ID', mail.get('headers'))
        if list_id:
            mailing_list = get_or_create_mailing_list(mail, subscription)
            message = get_or_create_message(mail)
            thread = get_or_create_thread(mail, mailing_list, message)


def get_or_create_message(mail):
    headers = mail.get('headers')
    message_id = get_header('Message-ID', headers)
    in_reply_to = get_header('In-Reply-To', headers)
    try:
        reply_message = Message.objects.get(message_id=in_reply_to)
    except:
        reply_message = None
    try:
        message = Message.objects.get(message_id=message_id)
    except:
        params = {
            'message_id': message_id,
            'subject': decode(get_header('Subject', headers)),
            'author': get_author(mail),
            'text': decode(mail.get('body')),
            'date_sent': to_date(get_header('Date', headers)),
            'in_reply_to': reply_message,
        }
        message = Message(**params)
        message.save()
    save_headers(message, headers)
    return message


def save_headers(message, headers):
    for header_name in get_headers(headers):
        value = get_header(header_name, headers)
        header_slug = slugify(header_name)
        header, created = Header.objects.get_or_create(
            slug=header_slug, defaults={'name': header_name})
        if type(value) == list:
            for val in value:
                mheader = MessageHeader(
                    header=header, message=message, value=val)
                mheader.save()
        else:
            mheader = MessageHeader(
                header=header, message=message, value=value)
            mheader.save()


def get_author(mail):
    from_header = parseaddr(get_header('From', mail.get('headers')))
    name = None
    if from_header[0] != '':
        name = decode(from_header[0])
    email = from_header[1]
    person, created = Person.objects.get_or_create(
        email=email, defaults={'name': name})
    return person


def get_or_create_thread(mail, mailing_list, message):
    message_id = get_header('Message-ID', mail.get('headers'))
    try:
        thread = message.get_thread()
        thread.date_last_message = message.date_sent
    except:
        date_last_message = to_date(get_header('Date', mail.get('headers')))
        params = {
            'subject': decode(get_header('Subject', mail.get('headers'))),
            'first_message': message, 'date_last_message': date_last_message,
            'mailing_list': mailing_list, }
        thread = Thread(**params)
    thread.save()
    return thread


def get_or_create_mailing_list(mail, subscription):
    list_id = get_header('List-ID', mail.get('headers'))
    try:
        mailing_list = MailingList.objects.get(list_id=list_id)
    except:
        headers = mail.get('headers')
        params = {
            'list_id': list_id,
            'list_post': get_header('List-Post', headers),
            'list_help': get_header('List-Help', headers),
            'list_archive': get_header('List-Archive', headers),
            'list_unsubscribe': get_header('List-Unsubscribe', headers),
            'list_type': guess_list_type(headers),
            'subscription': subscription, 'site': Site.objects.get_current()}
        mailing_list = MailingList(**params)
        mailing_list.save()
    return mailing_list


def has_header(header, headers):
    HRE = re.compile(r'^%s: ' % header, re.M + re.I)
    return bool(HRE.findall(headers))


def get_header(header, headers):
    HRE = re.compile(r'%s: (.+?)^[a-zA-Z\-]' % header, re.S + re.M + re.I)
    headers_found = [h.strip() for h in HRE.findall(headers)]
    if len(headers_found) == 1:
        return headers_found[0]
    return headers_found


def get_headers(headers):
    HRE = re.compile(r'^([a-zA-Z\-]+?): ', re.S + re.M + re.I)
    return HRE.findall(headers)


def guess_list_type(headers):
    from .choices import (GOOGLE_GROUPS, MAILINGLIST_OTHER, MAILMAN,
    YAHOO_GROUPS,)

    if 'googlegroups.com' in get_header('List-ID', headers):
        return GOOGLE_GROUPS
    if has_header('X-Mailman-Version', headers):
        return MAILMAN


def to_date(timestamp):
    return parser().parse(timestamp)


def decode(*args):
    quoted_printable_string = args[0]
    if len(args) == 2:
        encoding = args[1]
        if not encoding:
            encoding = 'latin1'
    else:
        return ' '.join([decode(*bit) for bit in decode_header(
            quoted_printable_string)])
    return unicodedata.normalize('NFC', unicode(decode_header(
        quoted_printable_string)[0][0], encoding=encoding, errors='ignore'))

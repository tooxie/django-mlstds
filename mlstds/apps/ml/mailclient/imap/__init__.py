# -*- coding: utf-8 -*-
from .exceptions import LoginError, FetchError, CommandUnknownError

import imaplib


class Client:
    def __init__(self, *ar, **kw):
        if kw.get('use_ssl'):
            self.client = imaplib.IMAP4_SSL(kw.get('host'), kw.get('port'))
        else:
            self.client = imaplib.IMAP4(kw.get('host'), kw.get('port'))
        self.login(kw.get('user'), kw.get('password'))
        mailboxes = kw.get('mailboxes')
        if mailboxes:
            self.mailboxes = [box.strip() for box in mailboxes.split(',')]
        else:
            self.mailboxes = ['INBOX']
        self.last_fetched = kw.get('last_fetched', 0)

    def fetchmail(self):
        mails = []
        for mailbox in self.mailboxes:
            self.client.select(mailbox)
            status, data = self.client.search(None, 'ALL')  # 'UNSEEN')
            if data[0]:
                for num in data[0].split():
                    header = self.fetch(num, '(BODY[HEADER])')
                    text = self.fetch(num, '(BODY[TEXT])')
                    mails.append({'headers': header[0][1], 'body': text[0][1]})
                    self.last_fetched = num
        self.client.close()
        self.client.logout()
        return [self.last_fetched, mails]

    def fetch(self, num, criterion):
        status, data = self.client.fetch(num, criterion)
        self.check_status(status, data)
        return data

    def check_status(self, status, data=None):
        if status == 'NO':
            raise FetchError(data)
        elif status == 'BAD':
            raise CommandUnknownError(data)

    def login(self, user, password):
        status, data = self.client.login(user, password)
        self.check_status(status, data)
        return True

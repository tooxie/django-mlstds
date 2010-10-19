# -*- coding: utf-8 -*-
import imp


def fetchmail(subscription):
    """
    Receives a Subscription object and fetches e-mail using an appropriate
    protocol.
    """
    if subscription.protocol:
        mod = __import__(subscription.protocol.lower(), globals(), locals(),
            ['Client'])
        Client = getattr(mod, 'Client')
    else:
        from client import Client
    params = {
        'host': subscription.host,
        'port': int(subscription.port),
        'user': subscription.user,
        'password': subscription.password,
        'use_ssl': subscription.use_ssl,
        'last_fetched': subscription.last_fetched,
        'mailboxes': subscription.mailboxes}
    return Client(**params).fetchmail()

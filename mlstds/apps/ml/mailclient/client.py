# -*- coding: utf-8 -*-


class Client:
    def __init__(self, host, port, user, password, use_ssl, protocol):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.use_ssl = use_ssl
        self.protocol = protocol

    def fetchmail(self):
        pass

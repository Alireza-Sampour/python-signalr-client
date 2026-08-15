#!/usr/bin/python
# -*- coding: utf-8 -*-

# signalr_aio/transports/_parameters.py
# Stanislav Lazarov

from json import dumps
from urllib.parse import urlencode, urlparse, urlunparse

import requests


class WebSocketParameters:
    def __init__(self, connection):
        self.protocol_version = '1.5'
        self.raw_url = self._clean_url(connection.url)
        self.conn_data = self._get_conn_data(connection.hub)
        self.session = connection.session or requests.Session()
        self.headers = dict(self.session.headers)
        self.socket_conf = None
        self._negotiate()
        self.socket_url = self._get_socket_url()

    @staticmethod
    def _clean_url(url):
        return url.rstrip('/')

    @staticmethod
    def _get_conn_data(hub):
        return dumps([{'name': hub}])

    @staticmethod
    def _format_url(url, action, query):
        return f'{url}/{action}?{query}'

    def _negotiate(self):
        query = urlencode({
            'connectionData': self.conn_data,
            'clientProtocol': self.protocol_version,
        })
        url = self._format_url(self.raw_url, 'negotiate', query)

        # Reuse the caller's session so authentication headers and cookies survive negotiation.
        request = self.session.get(url, timeout=30)
        request.raise_for_status()

        cookie = self._get_cookie_str(request.cookies)
        if cookie:
            self.headers['Cookie'] = cookie

        self.socket_conf = request.json()

        if 'ConnectionToken' not in self.socket_conf:
            raise RuntimeError(
                f'SignalR negotiate response did not contain ConnectionToken: '
                f'{self.socket_conf!r}'
            )

    @staticmethod
    def _get_cookie_str(request):
        return '; '.join(
            f'{name}={value}' for name, value in request.items()
        )

    def _get_socket_url(self):
        ws_url = self._get_ws_url_from()
        query = urlencode({
            'transport': 'webSockets',
            'connectionToken': self.socket_conf['ConnectionToken'],
            'connectionData': self.conn_data,
            'clientProtocol': self.socket_conf.get(
                'ProtocolVersion', self.protocol_version
            ),
        })

        return self._format_url(ws_url, 'connect', query)

    def _get_ws_url_from(self):
        parsed = urlparse(self.raw_url)
        scheme = 'wss' if parsed.scheme == 'https' else 'ws'
        url_data = (
            scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            parsed.query,
            parsed.fragment,
        )
        return urlunparse(url_data)

#!/usr/bin/python
# -*- coding: utf-8 -*-

# signalr_aio/_connection.py
# Stanislav Lazarov


from .events import EventHook
from .hubs import Hub
from .transports import Transport


class Connection:
    protocol_version = '1.5'

    def __init__(self, url, session=None):
        self.url = url
        self.__hubs = {}
        self.__send_counter = -1
        self.hub = None
        self.session = session
        self.received = EventHook()
        self.error = EventHook()
        self.__transport = Transport(self)
        self.started = False

        async def handle_error(**data):
            error = data.get('E')
            if error is not None:
                await self.error.fire(error)

        self.received += handle_error

    def start(self):
        if not self.__hubs:
            raise RuntimeError('Cannot start connection without a registered hub.')

        if self.started:
            return

        self.hub = next(iter(self.__hubs))
        self.__transport.start()

    def register_hub(self, name):
        if self.started:
            raise RuntimeError(
                'Cannot create new hub because connection is already started.')

        if name in self.__hubs:
            return self.__hubs[name]

        hub = Hub(name, self)
        self.__hubs[name] = hub
        return hub

    def increment_send_counter(self):
        self.__send_counter += 1
        return self.__send_counter

    def send(self, message):
        if not self.started and self.__transport.ws_loop.is_running():
            raise RuntimeError('Cannot send on a connection that has not started.')
        self.__transport.send(message)

    def close(self):
        if self.started:
            self.__transport.close()

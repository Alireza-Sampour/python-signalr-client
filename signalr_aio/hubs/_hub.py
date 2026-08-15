#!/usr/bin/python
# -*- coding: utf-8 -*-

# signalr_aio/hubs/_hub.py
# Stanislav Lazarov


class Hub:
    def __init__(self, name, connection):
        self.name = name
        self.server = HubServer(name, connection, self)
        self.client = HubClient(name, connection)


class HubServer:
    def __init__(self, name, connection, hub):
        self.name = name
        self.__connection = connection
        self.__hub = hub

    def invoke(self, method, *data):
        message = {
            'H': self.name,
            'M': method,
            'A': data,
            'I': self.__connection.increment_send_counter(),
        }
        self.__connection.send(message)


class HubClient:
    def __init__(self, name, connection):
        self.name = name
        self.__handlers = {}

        async def handle(**data):
            messages = data.get('M') or []
            for inner_data in messages:
                hub = inner_data.get('H', '')
                if hub.lower() != self.name.lower():
                    continue

                method = inner_data.get('M')
                handler = self.__handlers.get(method)
                if handler is None:
                    continue

                result = handler(inner_data.get('A'))
                if hasattr(result, '__await__'):
                    await result

        connection.received += handle

    def on(self, method, handler):
        """Register a handler for a server-to-client hub method."""
        handlers = self.__handlers.setdefault(method, [])
        if handler not in handlers:
            handlers.append(handler)

    def off(self, method, handler=None):
        """Remove one handler or all handlers for a hub method."""
        handlers = self.__handlers.get(method)
        if not handlers:
            return

        if handler is None:
            del self.__handlers[method]
            return

        if handler in handlers:
            handlers.remove(handler)

        if not handlers:
            del self.__handlers[method]

#!/usr/bin/python
# -*- coding: utf-8 -*-

# signalr_aio/events/_events.py
# Stanislav Lazarov

# Structure inspired by https://github.com/TargetProcess/signalr-client-py


class EventHook:
    def __init__(self):
        self._handlers = []

    def __iadd__(self, handler):
        if handler not in self._handlers:
            self._handlers.append(handler)
        return self

    def __isub__(self, handler):
        if handler in self._handlers:
            self._handlers.remove(handler)
        return self

    async def fire(self, *args, **kwargs):
        # Iterate over a snapshot so handlers can safely subscribe/unsubscribe while firing.
        for handler in tuple(self._handlers):
            result = handler(*args, **kwargs)
            if hasattr(result, '__await__'):
                await result

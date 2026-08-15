#!/usr/bin/python
# -*- coding: utf-8 -*-

# signalr_aio/transports/_transport.py
# Stanislav Lazarov

import asyncio

try:
    from ujson import dumps, loads
except ImportError:
    from json import dumps, loads

from websockets.asyncio.client import connect
from websockets.exceptions import ConnectionClosed

from ._parameters import WebSocketParameters
from ._queue_events import InvokeEvent, CloseEvent


class Transport:
    def __init__(self, connection):
        self._connection = connection
        self._ws_params = None
        self._conn_handler = None
        self.ws_loop = asyncio.new_event_loop()
        self.invoke_queue = asyncio.Queue()
        self.ws = None

    # ===================================
    # Public Methods

    def start(self):
        self._ws_params = WebSocketParameters(self._connection)
        self._connect()

        if not self.ws_loop.is_running():
            self.ws_loop.run_forever()

    def send(self, message):
        self._schedule(self.invoke_queue.put(InvokeEvent(message)))

    def close(self):
        self._schedule(self.invoke_queue.put(CloseEvent()))

    # -----------------------------------
    # Private Methods

    def _schedule(self, coroutine):
        # Support both calls made before the loop starts and calls from another thread.
        if self.ws_loop.is_running():
            return asyncio.run_coroutine_threadsafe(coroutine, self.ws_loop)
        return self.ws_loop.create_task(coroutine)

    def _connect(self):
        self._conn_handler = self.ws_loop.create_task(self._socket())

    async def _socket(self):
        async with connect(
            self._ws_params.socket_url,
            additional_headers=self._ws_params.headers,
        ) as self.ws:
            self._connection.started = True
            await self._master_handler(self.ws)

    async def _master_handler(self, ws):
        consumer_task = asyncio.create_task(self._consumer_handler(ws))
        producer_task = asyncio.create_task(self._producer_handler(ws))
        done, pending = await asyncio.wait(
            {consumer_task, producer_task},
            return_when=asyncio.FIRST_EXCEPTION,
        )

        for task in pending:
            task.cancel()

        await asyncio.gather(*pending, return_exceptions=True)

        # Propagate unexpected task failures instead of silently swallowing them.
        for task in done:
            if not task.cancelled():
                exception = task.exception()
                if exception is not None and not isinstance(exception, ConnectionClosed):
                    raise exception

    async def _consumer_handler(self, ws):
        try:
            async for message in ws:
                if message:
                    data = loads(message)
                    await self._connection.received.fire(**data)
        finally:
            self._connection.started = False

    async def _producer_handler(self, ws):
        while True:
            event = await self.invoke_queue.get()
            try:
                if event is None:
                    return

                if event.type == 'INVOKE':
                    await ws.send(dumps(event.message))
                elif event.type == 'CLOSE':
                    await ws.close()
                    self._connection.started = False
                    return
            finally:
                self.invoke_queue.task_done()

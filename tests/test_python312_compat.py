import asyncio

from signalr_aio import Connection
from signalr_aio.events import EventHook


def test_event_hook_supports_sync_and_async_handlers():
    hook = EventHook()
    received = []

    def sync_handler(value):
        received.append(('sync', value))

    async def async_handler(value):
        received.append(('async', value))

    hook += sync_handler
    hook += async_handler

    asyncio.run(hook.fire(42))

    assert received == [('sync', 42), ('async', 42)]


def test_event_hook_remove_is_safe():
    hook = EventHook()

    async def handler():
        pass

    hook -= handler
    hook += handler
    hook += handler
    hook -= handler
    hook -= handler
    hook -= handler

    assert hook._handlers == []


def test_connection_requires_a_hub():
    connection = Connection('https://example.com/signalr')

    try:
        connection.start()
    except RuntimeError as exc:
        assert 'registered hub' in str(exc)
    else:
        raise AssertionError('Connection.start() should require a registered hub')
    finally:
        connection._Connection__transport.ws_loop.close()

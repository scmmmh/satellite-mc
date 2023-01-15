"""Setup the Microdot server in asyncio mode."""
import uasyncio as asyncio

from microdot import Request
from microdot_asyncio import Microdot
from .signals import GermanHauptsignal

server = Microdot()
configured_signals = {}


async def shutdown(request: Request) -> None:
    """Shutdown the server.

    This ensures that all signals are switched off before stopping.
    """
    await asyncio.sleep(1)
    for signal in configured_signals.values():
        signal.set_signal({'state': 'off'})
    request.app.shutdown()


@server.delete('/')
async def delete_server(request: Request):  # noqa: ANN201
    """Delete the server, initiating a shutdown."""
    asyncio.create_task(shutdown(request))
    return None, 204


@server.patch('/signals/<uuid>')
async def patch_signal(request: Request, uuid: str):  # noqa: ANN201
    """Set a signal to the given state."""
    if uuid in configured_signals:
        signal = configured_signals[uuid]
        if signal.validate(request.json):
            signal.set_signal(request.json)
            return None, 204
        return None, 400
    return None, 404


def start_server() -> None:
    """Run the server, initialising the signals."""
    configured_signals['1'] = GermanHauptsignal(0, 1, 2)
    server.run(port=80)

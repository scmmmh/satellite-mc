"""System control API endpoints."""
import uasyncio as asyncio

from microdot import Request

from .base import server
from .signals import shutdown as signals_shutdown


API_SCHEMA = {
    'paths': {
        "/": {
            "delete": {
                "summary": "System: Shutdown",
                "description": "Shut down the system, powering off all attached devices.",
                "responses": {
                    "202": {
                        "description": "The shutdown process has started"
                    }
                }
            }
        }
    }
}


async def shutdown(request: Request) -> None:
    """Shutdown the server.

    This ensures that all signals are switched off before stopping.
    """
    await asyncio.sleep(1)
    signals_shutdown()
    request.app.shutdown()


@server.delete('/')
async def delete_server(request: Request):  # noqa: ANN201
    """Delete the server, initiating a shutdown."""
    asyncio.create_task(shutdown(request))
    return None, 202

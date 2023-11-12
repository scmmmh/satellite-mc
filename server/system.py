"""System control API endpoints."""
import machine

import uasyncio as asyncio

from microdot import Request

from .base import server
from .signals import shutdown as signals_shutdown
from .turnouts import shutdown as turnouts_shutdown
from __about__ import __version__


API_SCHEMA = {
    "paths": {
        "/api/system": {
            "get": {
                "summary": "System: Status",
                "description": "Retrieve the current system status.",
                "Responses": {
                    "200": {"description": "The current status of the system."}
                },
            },
            "delete": {
                "summary": "System: Shutdown",
                "description": "Shut down the system, powering off all attached devices.",
                "responses": {
                    "202": {"description": "The shutdown process has started"}
                },
            },
            "patch": {
                "summary": "System: Update",
                "description": "Update a single file on the system",
                "parameters": [
                    {
                        "name": "X-Filename",
                        "in": "header",
                        "required": True,
                        "description": "The filename to save the uploaded file at.",
                    },
                    {
                        "name": "Content-Length",
                        "in": "header",
                        "required": True,
                        "description": "The length of the uploaded file.",
                    },
                ],
                "requestBody": {
                    "description": "The file to upload",
                    "content": {"*/*": {}},
                    "required": True,
                },
                "responses": {
                    "204": {"description": "The file has been updated"},
                    "411": {
                        "description": "The Content-Length header must be specified"
                    },
                    "422": {"description": "The X-Filename header must be specified"},
                },
            },
        },
        "/api/system/restart": {
            "post": {
                "summary": "System: Restart",
                "description": "Restart the system",
                "Responses": {"202": {"description": "The restart has started."}},
            }
        },
    }
}


@server.get("/api/system")
async def get_system_status(request: Request):  # noqa: ANN201
    """Return the current system status."""
    return {"ready": True, "version": __version__}


async def shutdown(request: Request) -> None:
    """Shutdown the server.

    This ensures that all signals are switched off before stopping.
    """
    await asyncio.sleep(1)
    signals_shutdown()
    turnouts_shutdown()
    request.app.shutdown()


@server.delete("/api/system")
async def delete_server(request: Request):  # noqa: ANN201
    """Delete the server, initiating a shutdown."""
    asyncio.create_task(shutdown(request))
    return None, 202


@server.patch("/api/system")
async def patch_server(request: Request):  # noqa: ANN201
    """Patch the server updating a file."""
    if "X-Filename" in request.headers and "Content-Length" in request.headers:
        filename = request.headers["X-Filename"]
        size = int(request.headers["Content-Length"])

        with open(filename, "wb") as out_f:
            while size > 0:
                chunk = await request.stream.read(min(size, 1024))
                out_f.write(chunk)
                size -= len(chunk)

        return None, 204
    elif "Content-Length" not in request.headers:
        return None, 411
    else:
        return None, 422


async def restart(request: Request):  # noqa: ANN201
    """Restart the system by resetting it."""
    await shutdown(request)
    machine.reset()


@server.post("/api/system/restart")
async def restart_system(request: Request):  # noqa: ANN201
    """Request that the system restart."""
    asyncio.create_task(restart(request))
    return None, 202

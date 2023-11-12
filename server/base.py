"""Base server class for the API server."""
from machine import Pin
from microdot import Request, Response
from microdot_asyncio import Microdot
from microdot_cors import CORS


server = Microdot()
cors = CORS(server, allowed_origins="*")
busy = 0
busy_led = Pin("LED")


@server.before_request
def start_busy(request: Request):  # noqa: ANN201
    """Start indicating that the server is busy."""
    global busy
    busy = busy + 1
    busy_led.on()


@server.after_request
def stop_busy(request: Request, response: Response):  # noqa: ANN201
    """Stop indicating that the server is busy."""
    global busy
    busy = busy - 1
    if busy == 0:
        busy_led.off()

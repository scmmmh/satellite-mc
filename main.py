"""The main application."""

from server import start_server, shutdown_server
from utoolkit.wifi import connect


if connect(attempts=3):
    try:
        start_server()
    except KeyboardInterrupt:
        shutdown_server()

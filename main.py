"""The main application."""
from utoolkit.wifi import connect, disconnect

from server import start_server


if connect(3):
    start_server()
    disconnect()

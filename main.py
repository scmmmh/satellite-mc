"""The main application."""
from utoolkit.wifi import connect, disconnect

from server import start_server


if connect(3):
    print('Connected')
    start_server()
    disconnect()
    print('Shut down')
else:
    print('Connection failed')

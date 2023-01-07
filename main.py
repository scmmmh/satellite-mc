"""The main application."""
from utoolkit.wifi import connect, disconnect


if connect():
    print('Connected')
    disconnect()
else:
    print('Connection failed')

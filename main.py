"""The main application."""
from wifi import connect, disconnect


if connect():
    print('Connected')
    disconnect()
else:
    print('Connection failed')

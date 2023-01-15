"""Signal control API endpoints."""
from machine import Pin
from microdot import Request

from .base import server


API_SCHEMA = {
    'schemas': {
        'Signal':  {
            'type': 'object',
            'properties': {
                'id': {
                    'type': 'string'
                },
                'type': {
                    'type': 'String'
                },
                'params': {
                    'type': 'object',
                    'properties': {
                        '^S_': {
                            'type': 'string'
                        }
                    }
                },
                'state': {
                    'type': 'string'
                }
            }
        }
    },
    'paths': {
        '/api/signals': {
            'get': {
                'summary': 'Signals: List all',
                'description': 'List all configured signals.',
                'responses': {
                    '200': {
                        'description': 'A list of all available signals.',
                        'content': {
                            'application/json': {
                                'schema': {
                                    'type': 'array',
                                    'items': {
                                        '$ref': '#/components/schemas/Signal'
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        '/api/signals/{id}': {
            'summary': 'Single signal API endpoints',
            'parameters': [
                {
                    'name': 'id',
                    'in': 'path',
                    'description': 'The identifier of the signal to set',
                    'required': True,
                    'schema': {
                        'type': 'string'
                    },
                    'style': 'simple'
                }
            ],
            'get': {
                'summary': 'Signals: Get state',
                'description': 'Get the signal identified by the identifier',
                'responses': {
                    '200': {
                        'description': 'The requested signal object',
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': '#/components/schemas/Signal'
                                }
                            }
                        }
                    },
                    '404': {
                        'description': 'No signal exists for the given identifier',
                    }
                }
            },
            'patch': {
                'summary': 'Signals: Set state',
                'description': 'Set the signal to the required state.',
                'requestBody': {
                    'content': {
                        'application/json': {
                            'schema': {
                                'type': 'object',
                                'properties': {
                                    'state': {
                                        'description': 'The signal state to set',
                                        'type': 'string'
                                    }
                                }
                            }
                        }
                    }
                },
                'responses': {
                    '200': {
                        'description': 'Returns the updated signal state.',
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': '#/components/schemas/Signal'
                                }
                            }
                        }
                    },
                    '400': {
                        'description': 'The requested state is not valid'
                    },
                    '404': {
                        'description': 'The id does not identify an existing signal'
                    }
                }
            }
        }
    }
}


class GermanHauptsignal:
    """A German-style main signal.

    Supports the following states:

    * **off**: All lights off
    * **danger**: Red light only
    * **clear**: Green light only
    * **slow**: Green and yellow lights
    """

    def __init__(self: 'GermanHauptsignal', config: dict) -> None:
        """Initialise and set the signal to 'danger'."""
        self._config = config
        self._red = Pin(self._config['params']['red_pin'], Pin.OUT)
        self._green = Pin(self._config['params']['green_pin'], Pin.OUT)
        self._yellow = Pin(self._config['params']['yellow_pin'], Pin.OUT)
        self._state = ''
        self.set_signal({'state': 'danger'})

    def validate(self: 'GermanHauptsignal', body) -> bool:  # noqa: ANN001
        """Validate that the body is a valid instruction for this signal."""
        if body is not None and isinstance(body, dict):
            if 'state' in body and isinstance(body['state'], str):
                if body['state'] in ['off', 'danger', 'clear', 'slow']:
                    return True
        return False

    def set_signal(self: 'GermanHauptsignal', body: dict) -> None:
        """Set the signal to the state specified in the body."""
        if body['state'] == 'off':
            self._state = 'off'
            self._red.off()
            self._green.off()
            self._yellow.off()
        elif body['state'] == 'danger':
            self._state = 'danger'
            self._red.on()
            self._green.off()
            self._yellow.off()
        elif body['state'] == 'clear':
            self._state = 'clear'
            self._red.off()
            self._green.on()
            self._yellow.off()
        elif body['state'] == 'slow':
            self._state = 'slow'
            self._red.off()
            self._green.on()
            self._yellow.on()

    def as_json(self: 'GermanHauptsignal') -> dict:
        """Return this GermanHauptsignal in its JSON representation."""
        return {
            'id': self._config['id'],
            'type': 'GermanHauptsignal',
            'params': self._config['params'],
            'state': self._state
        }


signals = {}


@server.get('/api/signals')
async def get_all_signals(request: Request) -> list:
    """Return all configured signals."""
    return [signal.as_json() for signal in signals.values()]


@server.get('/api/signals/<id>')
async def get_signal(request: Request, id: str):  # noqa: ANN201
    """Get a single signal."""
    if id in signals:
        return signals[id].as_json()
    return None, 404


@server.patch('/api/signals/<id>')
async def patch_signal(request: Request, id: str):  # noqa: ANN201
    """Set a signal to the given state."""
    if id in signals:
        signal = signals[id]
        if signal.validate(request.json):
            signal.set_signal(request.json)
            return signal.as_json()
        return None, 400
    return None, 404


def add_signal(config: dict) -> None:
    """Add a signal to the set of available signals."""
    if config['type'] == 'GermanHauptsignal':
        signals[config['id']] = GermanHauptsignal(config)


def shutdown() -> None:
    """Shut down all signals."""
    for signal in signals.values():
        signal.set_signal({'state': 'off'})

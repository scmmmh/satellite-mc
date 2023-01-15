"""A set of signal types that can be controlled remotely."""
from machine import Pin


class GermanHauptsignal:
    """A German-style main signal.

    Supports the following states:

    * **off**: All lights off
    * **danger**: Red light only
    * **clear**: Green light only
    * **slow**: Green and yellow lights
    """

    def __init__(self: 'GermanHauptsignal', red_pin: int, green_pin: int, yellow_pin: int) -> None:
        """Initialise and set the signal to 'danger'."""
        self._red = Pin(red_pin, Pin.OUT)
        self._green = Pin(green_pin, Pin.OUT)
        self._yellow = Pin(yellow_pin, Pin.OUT)
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
            self._red.off()
            self._green.off()
            self._yellow.off()
        elif body['state'] == 'danger':
            self._red.on()
            self._green.off()
            self._yellow.off()
        elif body['state'] == 'clear':
            self._red.off()
            self._green.on()
            self._yellow.off()
        elif body['state'] == 'slow':
            self._red.off()
            self._green.on()
            self._yellow.on()

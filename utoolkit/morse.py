"""Simple morse blinking funcationality."""
from machine import Pin
from time import sleep


def blink(cmd: str, pin: str | int = 'LED', time_unit: float = 0.2) -> None:
    """Blink the pattern provided in `cmd`.

    Supported characters in the `cmd` are:

    * `.` - Short blink (1 time unit)
    * `-` - Long blink (3 time units)
    * ` ` - Short gap (intra-character - 3 time units)
    * `_` - Long gap (intra-word - 7 time units)

    The output pin to blink can be selected via the `pin` parameter and the
    length of a short blink via the `time_unit` parameter.
    """
    led = Pin(pin, Pin.OUT)
    led.off()
    for c in cmd:
        if c == '.':
            led.on()
            sleep(time_unit)
            led.off()
            sleep(time_unit)
        elif c == '-':
            led.on()
            sleep(time_unit * 3)
            led.off()
            sleep(time_unit)
        elif c == ' ':
            sleep(time_unit * 3)
        elif c == '_':
            sleep(time_unit * 7)

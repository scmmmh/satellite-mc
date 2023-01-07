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


MORSE_TABLE = {
    'A': '.-',
    'B': '-...',
    'C': '-.-.',
    'D': '-..',
    'E': '.',
    'F': '..-.',
    'G': '--.',
    'H': '....',
    'I': '..',
    'J': '.---',
    'K': '-.-',
    'L': '.-..',
    'M': '--',
    'N': '-.',
    'O': '---',
    'P': '.--.',
    'Q': '--.-',
    'R': '.-.',
    'S': '...',
    'T': '-',
    'U': '..-',
    'V': '...-',
    'W': '.--',
    'X': '-..-',
    'Y': '-.--',
    'Z': '--..',
    '1': '.----',
    '2': '..---',
    '3': '...--',
    '4': '....-',
    '5': '.....',
    '6': '-....',
    '7': '--...',
    '8': '---..',
    '9': '----.',
    '0': '-----',
}


def morse(text: str, pin: str | int = 'LED', time_unit: float = 0.2) -> None:
    """Blink the given `text` in morse code.

    Only supports letters A-z and digits 0-9.
    """
    text = text.upper()
    cmd = []
    for c in text:
        if c in MORSE_TABLE:
            cmd.append(MORSE_TABLE[c])
            cmd.append(' ')
        elif c == ' ':
            cmd.append('_')
    blink(''.join(cmd), pin=pin, time_unit=time_unit)

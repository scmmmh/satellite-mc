"""WIFI connection handling."""
from machine import Pin
from network import WLAN, STA_IF, STAT_CONNECTING, STAT_NO_AP_FOUND, STAT_WRONG_PASSWORD, STAT_CONNECT_FAIL
from time import sleep

from utoolkit.config import settings
from utoolkit.morse import blink


wlan = WLAN(STA_IF)
wlan.active(True)


def connect(attempts: int = 1) -> bool:
    """Connect to the WIFI network.

    Will attempt the connection `attempts` times.

    Requires the following two settings in the .env file:

    * WIFI.SSID: The network name
    * WIFI.PASSWORD: The network password

    Failures are indicated via LED blinking the following patterns 3 times:

    * ---: No WIFI configuration settings found
    * ...: No WIFI network found
    * .-.: Incorrect WIFI password
    * -.-: Any other connection error

    (`.` - short blink, `-` - long blink)
    """
    if 'WIFI' not in settings:
        blink('--- --- ---')
        return False

    activity = Pin("LED", Pin.OUT)
    activity.on()

    while attempts > 0:
        wlan.connect(ssid=settings["WIFI.SSID"], key=settings["WIFI.PASSWORD"])

        if "WIFI.HOSTNAME" in settings:
            wlan.config(hostname=settings["WIFI.HOSTNAME"])

        timeout = 30
        while not wlan.isconnected() and wlan.status() == STAT_CONNECTING and timeout > 0:
            activity.toggle()
            sleep(1)
            timeout = timeout - 1

        if wlan.isconnected():
            activity.off()
            return True
        else:
            activity.off()
            status = wlan.status()
            if status == STAT_NO_AP_FOUND:
                blink('... ... ...')
            elif status == STAT_WRONG_PASSWORD:
                blink('.-. .-. .-.')
            elif status == STAT_CONNECT_FAIL:
                blink('-.- -.- -.-')
        sleep(5)
        attempts = attempts - 1

    return False


def disconnect() -> None:
    """Disconnect from the WIFI network."""
    if wlan.isconnected():
        wlan.disconnect()

"""WIFI connection handling."""
from machine import Pin
from network import WLAN, STA_IF, STAT_CONNECTING, STAT_NO_AP_FOUND, STAT_WRONG_PASSWORD
from time import sleep

from env import settings
from util import repeat_blink


wlan = WLAN(STA_IF)
wlan.active(True)


def connect() -> bool:
    """Connect to the WIFI network.

    Requires the following two settings in the .env file:

    * WIFI.SSID: The network name
    * WIFI.PASSWORD: The network password

    Failures are indicated via LED blinking:

    * 2: No WIFI configuration settings found
    * 4: No WIFI network found
    * 6: Incorrect WIFI password
    * 8: Any other connection error
    """
    if 'WIFI' not in settings:
        repeat_blink(3, 2)
        return False

    activity = Pin("LED", Pin.OUT)
    activity.on()

    wlan.connect(settings['WIFI.SSID'], settings['WIFI.PASSWORD'])

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
            repeat_blink(3, 4)
        elif status == STAT_WRONG_PASSWORD:
            repeat_blink(3, 6)
        else:
            repeat_blink(3, 8)
        return False


def disconnect() -> None:
    """Disconnect from the WIFI network."""
    if wlan.isconnected():
        wlan.disconnect()

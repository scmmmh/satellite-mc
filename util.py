"""Utility functions."""
from machine import Pin
from time import sleep


activity = Pin('LED', Pin.OUT)


def blink(count: int, interval: float = 0.2) -> None:
    """Blink a given number of times."""
    activity.off()
    for _ in range(count * 2):
        activity.toggle()
        sleep(interval)
    activity.off()


def repeat_blink(repeat: int, count: int, interval: float = 0.2, repeat_interval: float = 1) -> None:
    """Run a repeat blink."""
    for _ in range(repeat):
        blink(count, interval=interval)
        sleep(repeat_interval)

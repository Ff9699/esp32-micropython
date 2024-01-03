"""Generic ESP32 320x240

"""

from machine import Pin, SPI
import st7789py as st7789

TFA = 40
BFA = 40
WIDE = 1
TALL = 0
SCROLL = 0      # orientation for scroll.py
FEATHERS = 1    # orientation for feathers.py

def config(rotation=0):
    """
    Configures and returns an instance of the ST7789 display driver.

    Args:
        rotation (int): The rotation of the display (default: 0).

    Returns:
        ST7789: An instance of the ST7789 display driver.
    """

    return st7789.ST7789(
        SPI(2, baudrate=40000000, sck=Pin(18), mosi=Pin(23), miso=None),
        240,
        240,
        reset=Pin(15, Pin.OUT),
        cs=Pin(5, Pin.OUT),
        dc=Pin(2, Pin.OUT),
        backlight=Pin(4, Pin.OUT),
        rotation=rotation)

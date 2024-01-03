import random
from machine import Pin, SPI
import st7789py
import vga2_bold_16x32 as font

# 创建spi协议对象
spi = SPI(2, baudrate=40000000, sck=Pin(18), mosi=Pin(23), miso=None)

# 创建显示屏对象,cs和dc参数Pin函数必须写全参数，不知道什么bug。
Pin(5, Pin.OUT).value(0)
tft=st7789py.ST7789(
        spi,
        240,
        240,
        reset=Pin(15, Pin.OUT),
        cs=Pin(5, Pin.OUT),
        dc=Pin(2, Pin.OUT),
        backlight=Pin(4, Pin.OUT),
        rotation=0)

# 屏幕显示红色
#tft.fill(st7789py.color565(255, 0, 0))

# 显示Hello
tft.text(font, "Hello", 0, 0, st7789py.color565(255, 0, 0), st7789py.color565(0, 0, 255))

"""
def show_text():
    for rotation in range(4):
        tft.rotation(rotation)
        tft.fill(0)
        col_max = tft.width - font.WIDTH*6
        row_max = tft.height - font.HEIGHT

        for _ in range(100):
            tft.text(
                font,
                "Hello!",
                random.randint(0, col_max),
                random.randint(0, row_max),
                st7789py.color565(random.getrandbits(8),random.getrandbits(8),random.getrandbits(8)),
                st7789py.color565(random.getrandbits(8),random.getrandbits(8),random.getrandbits(8))
            )

# 随机显示Hello!
# while True:
#    show_text()
"""

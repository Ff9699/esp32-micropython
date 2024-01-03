from machine import Pin, SPI
import st7789_itprojects


tft = st7789_itprojects.ST7889_Image(SPI(2, 60000000), dc=Pin(2), cs=Pin(5), rst=Pin(15))
tft.fill(st7789_itprojects.color565(0, 0, 0))  # 背景设置为黑色


def show_img():
    with open("text_img.dat", "rb") as f:
        for row in range(240):
            buffer = f.read(480)
            tft.show_img(0, row, 239, row, buffer)


show_img()
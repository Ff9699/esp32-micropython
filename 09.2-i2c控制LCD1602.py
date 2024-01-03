#使用lib_lcd1602_2004_with_i2c驱动，能在指定位置输出字符。
import time
from machine import SoftI2C, Pin
from lib_lcd1602_2004_with_i2c import LCD

scl_pin = 2
sda_pin = 15
lcd = LCD(SoftI2C(scl=Pin(scl_pin), sda=Pin(sda_pin), freq=100000))

lcd.clear()             #清屏
time.sleep(1)
#str="loading...1"
lcd.puts("loading....",0) #第一行
lcd.puts("by 111",1)       #第二行
for i in range(1,10):
    lcd.puts(str(i),0,10) #第0行10列
    time.sleep(1)


# SDA GPIO15
# SCL GPIO2
# Vcc 5V （3V显示不清楚）
# GND GND

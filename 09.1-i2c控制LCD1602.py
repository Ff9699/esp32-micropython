#使用esp32_i2c_1602lcd驱动。
import time
from machine import SoftI2C, Pin
from esp32_i2c_1602lcd import I2cLcd


DEFAULT_I2C_ADDR = 0x27
i2c = SoftI2C(sda=Pin(15),scl=Pin(2),freq=100000)
#i2c.scan()                                       #扫描i2c默认地址，即DEFAULT_I2C_ADDR，39即0x27
lcd = I2cLcd(i2c, DEFAULT_I2C_ADDR, 2, 16)

lcd.clear()             #清屏
lcd.blink_cursor_off()  #显示不闪烁光标
#str="loading...1"
lcd.putstr("loading....\n")
lcd.putstr("by 111")
for i in range(1,10):
    lcd.move_to(10,0) #移动光标到10列0行
    lcd.putstr(str(i))
    time.sleep(1)
'''
for i in range(1, 10):
    lcd.clear()                                   #清屏
    lcd.putstr("loading...{}\n".format(i))
    lcd.putstr("by 111")
    time.sleep(1)
'''

# SDA GPIO15
# SCL GPIO2
# Vcc 5V （3V显示不清楚）
# GND GND

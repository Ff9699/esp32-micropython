from machine import Pin
import time

p13 = Pin(13, Pin.OUT)

while True :
    p13.value(1)  # 吸合
    time.sleep(10)
    p13.value(0)  # 断开
    time.sleep(10)

from machine import Pin
import time


p15 = Pin(15, Pin.OUT)

for i in range(10):
    p15.value(1)  # 不响
    time.sleep(0.2)
    p15.value(0)  # 响
    time.sleep(0.2)

p15.value(1)  # 关闭


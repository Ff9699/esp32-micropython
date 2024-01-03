from machine import Pin
import time


p13 = Pin(13, Pin.IN)   #读取高低电平

while True:
    print(p13.value())
    time.sleep(0.1)

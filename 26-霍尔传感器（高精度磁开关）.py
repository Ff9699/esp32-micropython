from machine import Pin, ADC
import time


p15 = Pin(15, Pin.IN)

while True:
    print("p15:{}".format(p15.value()))
    time.sleep(0.1)

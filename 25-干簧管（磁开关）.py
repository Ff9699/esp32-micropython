from machine import Pin
import time


p15 = Pin(15, Pin.IN)

while True:
    if p15.value():
        print("无")
    else:
        print("有磁性物质靠近...")
    time.sleep(0.1)

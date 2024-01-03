from machine import Pin, PWM
import time

'''
led2 = PWM(Pin(2))
print("当前频率为"+str(led2.freq()))
led2.freq(1000)
print("当前频率为"+str(led2.freq()))
led2.duty(100)
print("当前占空比为"+str(led2.duty()))
'''

led2 = PWM(Pin(2))
led2.freq(1000)


while True:
    #变亮
    for i in range(0, 1024):
        led2.duty(i)
        print(led2.duty())
        time.sleep_ms(1)
    
    #变暗
    for i in range(1023, -1, -1):
        led2.duty(i)
        print(led2.duty())
        time.sleep_ms(1)
    time.sleep_ms(100)
    
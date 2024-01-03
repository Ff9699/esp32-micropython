'''
import machine
pin2 = machine.Pin(2,machine.Pin.OUT)
#pin2.value(1)
pin2.off()
'''
#从machine模块导入Pin类，用于操作GPIO引脚。
from machine import Pin
import time
p2 = Pin(2, Pin.OUT, value=1)#创建一个输出引脚对象p5，对应的是GPIO5，并在创建时将其设置为高电平。
'''
while True:
    time.sleep(1)
    p2.value(0)
    time.sleep(1)
    p2.value(1)
'''
for i in range(5):
    time.sleep(1)
    p2.value(0)
    time.sleep(1)
    p2.value(1)
    print(f"第{i+1}次循环")
#p2 = Pin(0, Pin.OUT)#创建一个输出引脚对象p2，对应的是GPIO2。
#p2.on()#将p2引脚设置为"on"（高电平）状态。
#p2.off()#将p2引脚设置为"off"（低电平）状态。
#p2.value(1)#将p2引脚设置为高电平。
from machine import Pin
import time

# 将引脚 13 定义为输入，引脚 2 定义为输出以控制 LED 灯
p13 = Pin(13, Pin.IN)  
led = Pin(2, Pin.OUT)  

# 定义名为 `fun` 的函数，以在调用时打开 LED 灯，等待 500 毫秒，然后关闭 LED 灯
def fun(*args):  
    print(f"上升沿触发,p13端口值为{p13.value()}")
    led.on()
    i=0
    while p13.value():
        #print(f"经过{i}ms")
        time.sleep(0.1)
        i+=100
    print(f"经过{i}ms,p13端口值为{p13.value()}")
    led.off()
    time.sleep(1)
    #led.off()
def fun1(*args):  
    print("下降沿触发")
    #led.on()
    time.sleep(2)
    #led.off()
# 在引脚 13 上设置中断请求（IRQ），以在上升信号时触发 `fun` 函数
p13.irq(fun,Pin.IRQ_RISING)      #定义中断·上升沿触发
#p13.irq(fun1,Pin.IRQ_FALLING)   #无法触发不同函数。
for i in range(100):
    print(i)
    time.sleep(0.5)

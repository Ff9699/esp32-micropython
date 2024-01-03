from machine import Pin, ADC
import time


# 模拟量
sound_analog = ADC(Pin(33))
sound_analog.atten(ADC.ATTN_11DB)  # 这里配置测量量程为3.3V


def handle_sound(*argc):
    # print(argc)
    print("有声音...")


# 数字量
p15 = Pin(15, Pin.IN)
#配置中断函数，在pin15收到上升沿信号时中断，
#传感器无声音输出0，有声音输出1，所以配置上升沿中断。
p15.irq(trigger=Pin.IRQ_RISING, handler=handle_sound) 

# 循环检测
while True:
    sound_value = sound_analog.read()  # 0-4095
    print(sound_value)
    time.sleep(0.1)

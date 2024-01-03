from machine import Pin, ADC
import time


# 模拟量
ps2_y = ADC(Pin(33))
ps2_y.atten(ADC.ATTN_11DB)  # 这里配置测量量程为3.3V

# 数字量
p15 = Pin(15, Pin.IN)

# 循环检测
while True:
    val_y = ps2_y.read()  # 0-4095
    light = p15.value()
    print(val_y, light)
    time.sleep(0.1)

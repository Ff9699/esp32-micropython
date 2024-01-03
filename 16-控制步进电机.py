from machine import Pin  # 从machine模块导入Pin类
import time  # 导入time模块

pins = [Pin(pin, Pin.OUT) for pin in [15, 2, 4, 16]]  # 创建包含4个Pin.OUT引脚的列表
values = [(1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)]  # 定义4种值的元组列表
delay_time_ms = 10  # 设置延迟时间为500毫秒

while True:  # 进入无限循环
    for value in values:  # 遍历values列表
        for pin, val in zip(pins, value):  # 使用zip函数同时遍历pins和value，zip将两个列表中的元素一一配对
            pin.value(val)  # 设置引脚值
        time.sleep_ms(delay_time_ms)  # 延迟一段时间

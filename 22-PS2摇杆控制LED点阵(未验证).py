from machine import Pin, ADC
import time


# 点阵对应引脚
row_1 = Pin(32, Pin.OUT)
row_2 = Pin(33, Pin.OUT)
row_3 = Pin(25, Pin.OUT)
row_4 = Pin(26, Pin.OUT)
row_5 = Pin(27, Pin.OUT)
row_6 = Pin(14, Pin.OUT)
row_7 = Pin(12, Pin.OUT)
row_8 = Pin(13, Pin.OUT)

row_list = [row_1, row_2, row_3, row_4, row_5, row_6, row_7, row_8]

col_1 = Pin(21, Pin.OUT)
col_2 = Pin(19, Pin.OUT)
col_3 = Pin(18, Pin.OUT)
col_4 = Pin(5, Pin.OUT)
col_5 = Pin(17, Pin.OUT)
col_6 = Pin(16, Pin.OUT)
col_7 = Pin(4, Pin.OUT)
col_8 = Pin(2, Pin.OUT)


col_list = [col_1, col_2, col_3, col_4, col_5, col_6, col_7, col_8]


def set_power_row(i):
    for row in row_list:
        row.value(0)
    if 0 <= i <= 7:
        row_list[i].value(1)


def set_earth_col(i):
    for col in col_list:
        col.value(1)
    if 0 <= i <= 7:
        col_list[i].value(0)


def set_col_row_led_light(row, col):
    set_power_row(row)
    set_earth_col(col)


# PS2摇杆引脚
ps2_y = ADC(Pin(34))
ps2_y.atten(ADC.ATTN_11DB)  # 这里配置测量量程为3.3V
ps2_x = ADC(Pin(35))
ps2_x.atten(ADC.ATTN_11DB)  # 这里配置测量量程为3.3V

# PS2按下引脚
btn = Pin(15, Pin.IN)

# 点亮的LED灯
x = 0
y = 0

# 程序主循环
while True:
    val_y = ps2_y.read()  # 0-4095
    val_x = ps2_x.read()  # 0-4095
    # print("x:{} y:{} btn:{}".format(val_x, val_y, btn.value()))
    if val_y > 2000:
        y -= 1
        if y < 0:
            y = 0
    elif val_y < 1600:
        y += 1
        if y > 7:
            y = 7
    
    if val_x > 2000:
        x -= 1
        if x < 0:
            x = 0
    elif val_x < 1600:
        x += 1
        if x > 7:
            x = 7
    
    print(x, y)
    set_col_row_led_light(x, y)
            
    time.sleep(0.1)

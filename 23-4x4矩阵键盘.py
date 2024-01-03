from machine import Pin
import time


#row1 = Pin(19, Pin.OUT)
#row2 = Pin(18, Pin.OUT)
#row3 = Pin(5, Pin.OUT)
#row4 = Pin(17, Pin.OUT)
#row_list = [row1, row2, row3, row4]
row_list = [Pin(pin, Pin.OUT) for pin in [19,18,5,17]]  #压缩代码

col1 = Pin(16, Pin.IN, Pin.PULL_DOWN)
col2 = Pin(4, Pin.IN, Pin.PULL_DOWN)
col3 = Pin(2, Pin.IN, Pin.PULL_DOWN)
col4 = Pin(15, Pin.IN, Pin.PULL_DOWN)
col_list = [col1, col2, col3, col4]

names = [
    ["1", "2", "3", "A"],
    ["4", "5", "6", "B"],
    ["7", "8", "9", "C"],
    ["*", "0", "#", "D"]
]

while True:
    for i, row in enumerate(row_list):
        for temp in row_list:           #设置其余低电平
            temp.value(0)
        row.value(1)
        time.sleep_ms(10)
        for j, col in enumerate(col_list):
            if col.value() == 1:
                print("按键: {} 被按下".format(names[i][j]))
        # print(row1.value(), row2.value(), row3.value(), row4.value())
        # print(col1.value(), col2.value(), col3.value(), col4.value())
        # print("-" * 30)
                
    time.sleep(0.1)

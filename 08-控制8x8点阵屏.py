#程序行row为高电平，列col为低电平时，灯亮。
import machine
import time

row_1 = machine.Pin(32, machine.Pin.OUT)
row_2 = machine.Pin(33, machine.Pin.OUT)
row_3 = machine.Pin(25, machine.Pin.OUT)
row_4 = machine.Pin(26, machine.Pin.OUT)
row_5 = machine.Pin(27, machine.Pin.OUT)
row_6 = machine.Pin(14, machine.Pin.OUT)
row_7 = machine.Pin(12, machine.Pin.OUT)
row_8 = machine.Pin(13, machine.Pin.OUT)

row_list = [row_1, row_2, row_3, row_4, row_5, row_6, row_7, row_8]


col_1 = machine.Pin(19, machine.Pin.OUT)
col_2 = machine.Pin(18, machine.Pin.OUT)
col_3 = machine.Pin(5, machine.Pin.OUT)
col_4 = machine.Pin(17, machine.Pin.OUT)
col_5 = machine.Pin(16, machine.Pin.OUT)
col_6 = machine.Pin(4, machine.Pin.OUT)
col_7 = machine.Pin(2, machine.Pin.OUT)
col_8 = machine.Pin(15, machine.Pin.OUT)

col_list = [col_1, col_2, col_3, col_4, col_5, col_6, col_7, col_8]


def set_power_row(i):
    #让所有行设置为低电压。
    for row in row_list:#
        row.value(0)
    #设置目的列为高电平。
    if 0 <= i <= 7:
        row_list[i].value(1)


def set_earth_col(i):
    #让所有列设置为高电压。
    for col in col_list:
        col.value(1)
    #设置目的列为低电平。
    if 0 <= i <= 7:
        col_list[i].value(0)


def show_liushuideng():
    # 流水灯
    for row in range(8):
        set_power_row(row)
        for col in range(8):
            set_earth_col(col)
            time.sleep_ms(50)

'''
def show_light(row,col):
    row_list[row].value(1)
    col_list[col].value(0)
'''

def show_arrow():
    # 箭头图形
    img_list = [
        (1, 4),
        (2, 5),
        (3, 6),
        (4, 0), (4, 1), (4, 2), (4, 3), (4, 4), (4, 5), (4, 6), (4, 7),
        (5, 6),
        (6, 5),
        (7, 4)
    ]

    # 让箭头从左向右移动
    while True:
        for i in range(-7, 8):
            for j in range(6):             #控制箭头速度。
                for row, col in img_list:
                    set_power_row(row)
                    set_earth_col(col + i)
                    time.sleep_us(900)     #延时时间为led灯暗到亮的时间，防止运行太快，灯还没亮就灭了。
            #time.sleep_ms(10)
        


    
if __name__ == "__main__":
    show_liushuideng()
    show_arrow()
    '''
    img_list = [
        (1, 4),
        (2, 5),
        (3, 6),
        (4, 0), (4, 1), (4, 2), (4, 3), (4, 4), (4, 5), (4, 6), (4, 7),
        (5, 6),
        (6, 5),
        (7, 4)
    ]
    while True :
        for row, col in img_list:
            set_power_row(row)
            set_earth_col(col)
            time.sleep_us(900)
'''
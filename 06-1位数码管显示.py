import machine
import time


a = machine.Pin(13, machine.Pin.OUT)
b = machine.Pin(12, machine.Pin.OUT)
c = machine.Pin(14, machine.Pin.OUT)
d = machine.Pin(27, machine.Pin.OUT)
e = machine.Pin(26, machine.Pin.OUT)
f = machine.Pin(25, machine.Pin.OUT)
g = machine.Pin(33, machine.Pin.OUT)
dot = machine.Pin(32, machine.Pin.OUT)

'''
a.on()
b.on()
c.on()
d.on()
e.on()
f.on()
g.on()
dot.on()
'''

#创建led对象列表
led_list = [a, b, c, d, e, f, g, dot]

#创建字典，键：要显示的数字；键值：对应led灯的亮灭。
number_dict = {
    0: "11111100",
    1: "01100000",
    2: "11011010",
    3: "11110010",
    4: "01100110",
    5: "10110110",
    6: "10111110",
    7: "11100000",
    8: "11111110",
    9: "11110110",
    "open": "11111111",
    "close": "00000000"
}

def show_number(number):
    if number_dict.get(number):#字典取值，判断字典中是否有对应键。
        i = 0                              #第几个led
        for bit in number_dict.get(number):#字典取值
            if bit == "1":                 #亮
                led_list[i].value(1)
            else:                          #灭
                led_list[i].value(0)
            i += 1

def main():
    show_number("open")  # 全亮
    time.sleep(1)
    show_number("close")  # 全灭
    time.sleep(1)
    
    i = 0
    while True:
        show_number(i)
        i += 1
        if i >= 10:
            i -=10
        time.sleep(0.5)
    '''
    for i in range(10):
        show_number(i)
        time.sleep(0.5)
    '''
if __name__ == "__main__":
    main()
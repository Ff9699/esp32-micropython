#单个数码管显示时间太短，没有全量就关闭，整体亮度会降低
import machine
import time

led1 = machine.Pin(5, machine.Pin.OUT)
led2 = machine.Pin(18, machine.Pin.OUT)
led3 = machine.Pin(19, machine.Pin.OUT)
led4 = machine.Pin(21, machine.Pin.OUT)
'''
led1.value(0)
led2.value(0)
led3.value(0)
led4.value(0)
'''
#创建4个数码管对象列表
led_light_list = [led1, led2, led3, led4]


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

def led_light_on(i):
    '''
    点亮第i个数码管
    '''
    #使用数码管为共阴极，设置成高电平时，无压降。
    for led in led_light_list:
        led.value(1)
    led_light_list[i].value(0)

def show_4_number(number):
    '''
    显示四位整数
    '''
    if 0 <= number <= 9999:
        i = 0
        for num in "%04d" % number:#整数转换成字符串，字符串可以遍历，整数不行。
            #print(num)
            show_number(int(num))#回转成整数。
            led_light_on(i)
            time.sleep_ms(5)
            i += 1
            
def main():
    for led in led_light_list:
            led.value(0)
    show_number("open")  # 全亮
    time.sleep(1)
    show_number("close")  # 全灭
    time.sleep(1)
    
    #show_4_number(1234)
    for i in range(1000, 10000):
        for j in range(10):
            show_4_number(i)
            
if __name__ == "__main__":
    main()
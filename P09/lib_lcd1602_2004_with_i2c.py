'''
    mpy驱动程序用于I2C LCD1602
    作者：shaoziyang
    日期：2018.2
    http://www.micropython.org.cn
'''
import time
from machine import SoftI2C, Pin


class LCD():
    def __init__(self, i2c):

        # 板定义
        # P0: RS
        # P1: R/W
        # P2: E
        # P3: --
        # P4-P7: DB4-DB7

        self.i2c = i2c
        print('(Re)初始化...')
        scan_result = i2c.scan()
        while not scan_result:
            print("无法定位I2C设备")
            time.sleep_ms(10)
            scan_result = i2c.scan()
        self.LCD_I2C_ADDR = i2c.scan()[0]
        self.bufs = []  # 一个字节列表，一次性用i2c.writeto写入所有内容比写入每个字节更有效
        self.BK = 0x08
        self.RS = 0x00
        self.E = 0x04

        self.queue(0x30)  # 0011
        self.execute()
        time.sleep_ms(5)
        self.queue(0x30)  # 0011
        self.execute()
        time.sleep_ms(5)
        self.queue(0x20)  # 0010
        self.execute()
        time.sleep_ms(5)
        self.add_command(0x28,run=True)  # 0010   1000
        self.on()
        self.add_command(0x06)  # 0000   0110
        self.add_command(0x01)  # 0000   0001
        self.execute()

    def queue(self, dat):
        '''
        将数据添加到队列，等待执行
        :param dat: 8位数据，前4位是D7-D4，后4位是NC, E, RW, RS
        :return:
        '''
        
        dat = dat & 0xF0
        dat |= self.BK
        dat |= self.RS
        
        self.bufs.append(dat | 0x04) # enable high
        self.bufs.append(dat) # enable low
            
    def execute(self):
        try:
            bytearray_to_write = bytearray(len(self.bufs))
            for i in range(len(self.bufs)):
                bytearray_to_write[i] = self.bufs[i]
            self.i2c.writeto(self.LCD_I2C_ADDR, bytearray_to_write)
            self.bufs=[]
            time.sleep_us(50)
        except Exception as e:
            print(e)

    def add_command(self, cmd, run=False):
        self.RS = 0
        # I2C芯片只有8位，所以只有4位可以用于数据，因此数据需要分两部分发送
        self.queue(cmd)
        self.queue(cmd << 4)
        if run:
            self.execute()

    def add_data(self, dat):
        self.RS = 1
        # I2C芯片只有8位，所以只有4位可以用于数据，因此数据需要分两部分发送
        self.queue(dat)
        self.queue(dat << 4)

    def clear(self):
        self.add_command(1,run=True)

    def backlight(self, on):
        if on:
            self.BK = 0x08
        else:
            self.BK = 0
        self.add_command(0,run=True)

    def on(self):
        self.add_command(0x0C,run=True)  # 0000 1100 打开屏幕，关闭光标，关闭闪烁

    def off(self):
        self.add_command(0x08,run=True)  # 0000 1000 关闭屏幕，关闭光标，关闭闪烁

    def shl(self):
        self.add_command(0x18,run=True)

    def shr(self):
        self.add_command(0x1C,run=True)

    def char(self, ch, x=-1, y=0):
        if x >= 0:
            if y == 0:
                a = 0x80
            if y == 1:
                a = 0xC0
            if y == 2:
                a = 0x80 + 20
            if y == 3:
                a = 0xC0 + 20
            a += x
            self.add_command(a)
        self.add_data(ch)

    def puts(self, s, y=0, x=0):
        '''

        :param s: 字符串，仅限ascii
        :param y: 行（你需要自己写合理的数字到这个参数）
        :param x: 列（你需要自己写合理的数字到这个参数）
        :return:
        '''
        try:
            if len(s) > 0:
                self.char(ord(s[0]), x, y)
                for i in range(1, len(s)):
                    self.char(ord(s[i]))
        except Exception as e:
            print(e)
        self.execute()

    def create_charactor(self, ram_position, char):
        '''

        :param position: int, 0-7
        :param char: 8字节
        :return:
        '''

        assert len(char)==8
        ram_position &= 0x7;
        set_CGRAM_address = 0x40
        self.add_command(set_CGRAM_address | (ram_position << 3))
        for i in range(8):
            self.add_data(char[i])
        self.execute()

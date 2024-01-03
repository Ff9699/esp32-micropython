"""实现通过PCF8574在I2C上连接的HD44780字符LCD。
   这是在以下链接进行测试的：https://www.wemos.cc/product/d1-mini.html"""

from lcd_api import LcdApi  # 导入LcdApi模块
from machine import I2C  # 导入I2C模块
from time import sleep_ms  # 导入sleep_ms模块

# 定义PCF8574连接到各种LCD线的移位或掩码

MASK_RS = 0x01  # 定义MASK_RS为0x01
MASK_RW = 0x02  # 定义MASK_RW为0x02
MASK_E = 0x04  # 定义MASK_E为0x04
SHIFT_BACKLIGHT = 3  # 定义SHIFT_BACKLIGHT为3
SHIFT_DATA = 4  # 定义SHIFT_DATA为4


class I2cLcd(LcdApi):  # 定义I2cLcd类，继承自LcdApi
    """实现通过PCF8574在I2C上连接的HD44780字符LCD。"""

    def __init__(self, i2c, i2c_addr, num_lines, num_columns):  # 初始化函数
        self.i2c = i2c  # 定义i2c
        self.i2c_addr = i2c_addr  # 定义i2c地址
        self.i2c.writeto(self.i2c_addr, bytearray([0]))  # 写入i2c地址
        sleep_ms(20)   # 允许LCD启动时间
        # 发送重置3次
        self.hal_write_init_nibble(self.LCD_FUNCTION_RESET)  # 写入初始化半字节
        sleep_ms(5)    # 需要延迟至少4.1毫秒
        self.hal_write_init_nibble(self.LCD_FUNCTION_RESET)  # 再次写入初始化半字节
        sleep_ms(1)
        self.hal_write_init_nibble(self.LCD_FUNCTION_RESET)  # 再次写入初始化半字节
        sleep_ms(1)
        # 将LCD放入4位模式
        self.hal_write_init_nibble(self.LCD_FUNCTION)  # 写入初始化半字节
        sleep_ms(1)
        LcdApi.__init__(self, num_lines, num_columns)  # 初始化LcdApi
        cmd = self.LCD_FUNCTION  # 定义cmd
        if num_lines > 1:  # 如果行数大于1
            cmd |= self.LCD_FUNCTION_2LINES  # cmd或等于LCD_FUNCTION_2LINES
        self.hal_write_command(cmd)  # 写入命令

    def hal_write_init_nibble(self, nibble):  # 定义hal_write_init_nibble函数
        """向LCD写入初始化半字节。

        这个特定的函数只在初始化期间使用。
        """
        byte = ((nibble >> 4) & 0x0f) << SHIFT_DATA  # 定义byte
        self.i2c.writeto(self.i2c_addr, bytearray([byte | MASK_E]))  # 写入i2c地址
        self.i2c.writeto(self.i2c_addr, bytearray([byte]))  # 写入i2c地址

    def hal_backlight_on(self):  # 定义hal_backlight_on函数
        """允许hal层打开背光。"""
        self.i2c.writeto(self.i2c_addr, bytearray([1 << SHIFT_BACKLIGHT]))  # 写入i2c地址

    def hal_backlight_off(self):  # 定义hal_backlight_off函数
        """允许hal层关闭背光。"""
        self.i2c.writeto(self.i2c_addr, bytearray([0]))  # 写入i2c地址

    def hal_write_command(self, cmd):  # 定义hal_write_command函数
        """向LCD写入命令。

        数据在E的下降沿上锁存。
        """
        byte = ((self.backlight << SHIFT_BACKLIGHT) | (((cmd >> 4) & 0x0f) << SHIFT_DATA))  # 定义byte
        self.i2c.writeto(self.i2c_addr, bytearray([byte | MASK_E]))  # 写入i2c地址
        self.i2c.writeto(self.i2c_addr, bytearray([byte]))  # 写入i2c地址
        byte = ((self.backlight << SHIFT_BACKLIGHT) | ((cmd & 0x0f) << SHIFT_DATA))  # 定义byte
        self.i2c.writeto(self.i2c_addr, bytearray([byte | MASK_E]))  # 写入i2c地址
        self.i2c.writeto(self.i2c_addr, bytearray([byte]))  # 写入i2c地址
        if cmd <= 3:  # 如果cmd小于等于3
            # home和clear命令需要最坏的延迟4.1毫秒
            sleep_ms(5)  # 延迟5毫秒

    def hal_write_data(self, data):  # 定义hal_write_data函数
        """向LCD写入数据。"""
        byte = (MASK_RS | (self.backlight << SHIFT_BACKLIGHT) | (((data >> 4) & 0x0f) << SHIFT_DATA))  # 定义byte
        self.i2c.writeto(self.i2c_addr, bytearray([byte | MASK_E]))  # 写入i2c地址
        self.i2c.writeto(self.i2c_addr, bytearray([byte]))  # 写入i2c地址
        byte = (MASK_RS | (self.backlight << SHIFT_BACKLIGHT) | ((data & 0x0f) << SHIFT_DATA))  # 定义byte
        self.i2c.writeto(self.i2c_addr, bytearray([byte | MASK_E]))  # 写入i2c地址
        self.i2c.writeto(self.i2c_addr, bytearray([byte]))  # 写入i2c地址



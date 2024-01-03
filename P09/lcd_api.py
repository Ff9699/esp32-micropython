"""提供与HD44780兼容的字符LCD交互的API。"""

import time

class LcdApi:
    """实现与HD44780兼容的字符LCD交互的API。
    这个类只知道要发送给LCD的命令，不知道如何将它们发送给LCD。

    预期派生类将实现hal_xxx函数。
    """

    # 以下常量名称来自avrlib lcd.h
    # 头文件，但是，我将定义从位号
    # 改为位掩码。
    #
    # HD44780 LCD控制器命令集

    LCD_CLR = 0x01              # DB0: 清除显示
    LCD_HOME = 0x02             # DB1: 返回到起始位置

    LCD_ENTRY_MODE = 0x04       # DB2: 设置输入模式
    LCD_ENTRY_INC = 0x02        # --DB1: 增量
    LCD_ENTRY_SHIFT = 0x01      # --DB0: 移位

    LCD_ON_CTRL = 0x08          # DB3: 打开lcd/光标
    LCD_ON_DISPLAY = 0x04       # --DB2: 打开显示
    LCD_ON_CURSOR = 0x02        # --DB1: 打开光标
    LCD_ON_BLINK = 0x01         # --DB0: 光标闪烁

    LCD_MOVE = 0x10             # DB4: 移动光标/显示
    LCD_MOVE_DISP = 0x08        # --DB3: 移动显示 (0-> 移动光标)
    LCD_MOVE_RIGHT = 0x04       # --DB2: 向右移动 (0-> 向左)

    LCD_FUNCTION = 0x20         # DB5: 功能设置
    LCD_FUNCTION_8BIT = 0x10    # --DB4: 设置8BIT模式 (0->4BIT模式)
    LCD_FUNCTION_2LINES = 0x08  # --DB3: 两行 (0->一行)
    LCD_FUNCTION_10DOTS = 0x04  # --DB2: 5x10字体 (0->5x7字体)
    LCD_FUNCTION_RESET = 0x30   # 参见"通过指令初始化"部分

    LCD_CGRAM = 0x40            # DB6: 设置CG RAM地址
    LCD_DDRAM = 0x80            # DB7: 设置DD RAM地址

    LCD_RS_CMD = 0
    LCD_RS_DATA = 1

    LCD_RW_WRITE = 0
    LCD_RW_READ = 1

    def __init__(self, num_lines, num_columns):
        self.num_lines = num_lines
        if self.num_lines > 4:
            self.num_lines = 4
        self.num_columns = num_columns
        if self.num_columns > 40:
            self.num_columns = 40
        self.cursor_x = 0
        self.cursor_y = 0
        self.backlight = True
        self.display_off()
        self.backlight_on()
        self.clear()
        self.hal_write_command(self.LCD_ENTRY_MODE | self.LCD_ENTRY_INC)
        self.hide_cursor()
        self.display_on()

    def clear(self):
        """清除LCD显示并将光标移动到左上角。"""
        self.hal_write_command(self.LCD_CLR)
        self.hal_write_command(self.LCD_HOME)
        self.cursor_x = 0
        self.cursor_y = 0

    def show_cursor(self):
        """使光标可见。"""
        self.hal_write_command(self.LCD_ON_CTRL | self.LCD_ON_DISPLAY |
                               self.LCD_ON_CURSOR)

    def hide_cursor(self):
        """使光标隐藏。"""
        self.hal_write_command(self.LCD_ON_CTRL | self.LCD_ON_DISPLAY)

    def blink_cursor_on(self):
        """打开光标，并使其闪烁。"""
        self.hal_write_command(self.LCD_ON_CTRL | self.LCD_ON_DISPLAY |
                               self.LCD_ON_CURSOR | self.LCD_ON_BLINK)

    def blink_cursor_off(self):
        """打开光标，并使其不闪烁（即为实心）。"""
        self.hal_write_command(self.LCD_ON_CTRL | self.LCD_ON_DISPLAY |
                               self.LCD_ON_CURSOR)

    def display_on(self):
        """打开（即取消屏蔽）LCD。"""
        self.hal_write_command(self.LCD_ON_CTRL | self.LCD_ON_DISPLAY)

    def display_off(self):
        """关闭（即屏蔽）LCD。"""
        self.hal_write_command(self.LCD_ON_CTRL)

    def backlight_on(self):
        """打开背光。

        这不是真正的LCD命令，但是一些模块有背光控制，
        所以这允许hal通过命令。
        """
        self.backlight = True
        self.hal_backlight_on()

    def backlight_off(self):
        """关闭背光。

        这不是真正的LCD命令，但是一些模块有背光控制，
        所以这允许hal通过命令。
        """
        self.backlight = False
        self.hal_backlight_off()

    def move_to(self, cursor_x, cursor_y):
        """将光标位置移动到指定位置。光标位置是从零开始的
        （即cursor_x == 0表示第一列）。
        """
        self.cursor_x = cursor_x
        self.cursor_y = cursor_y
        addr = cursor_x & 0x3f
        if cursor_y & 1:
            addr += 0x40    # 行1 & 3加0x40
        if cursor_y & 2:
            addr += 0x14    # 行2 & 3加0x14
        self.hal_write_command(self.LCD_DDRAM | addr)

    def putchar(self, char):
        """在当前光标位置向LCD写入指定字符，并将光标位置向前移动一个位置。"""
        if char != '\n':
            self.hal_write_data(ord(char))
            self.cursor_x += 1
        if self.cursor_x >= self.num_columns or char == '\n':
            self.cursor_x = 0
            self.cursor_y += 1
            if self.cursor_y >= self.num_lines:
                self.cursor_y = 0
            self.move_to(self.cursor_x, self.cursor_y)

    def putstr(self, string):
        """在当前光标位置向LCD写入指定字符串，并适当地移动光标位置。"""
        for char in string:
            self.putchar(char)

    def custom_char(self, location, charmap):
        """将字符写入8个CGRAM位置之一，可用作
        chr(0)到chr(7)。
        """
        location &= 0x7
        self.hal_write_command(self.LCD_CGRAM | (location << 3))
        time.sleep_us(40)
        for i in range(8):
            self.hal_write_data(charmap[i])
            time.sleep_us(40)
        self.move_to(self.cursor_x, self.cursor_y)

    def hal_backlight_on(self):
        """允许hal层打开背光。

        如果需要，派生的HAL类将实现此函数。
        """
        pass

    def hal_backlight_off(self):
        """允许hal层关闭背光。

        如果需要，派生的HAL类将实现此函数。
        """
        pass

    def hal_write_command(self, cmd):
        """向LCD写入命令。

        预期派生的HAL类将实现此函数。
        """
        raise NotImplementedError

    def hal_write_data(self, data):
        """向LCD写入数据。

        预期派生的HAL类将实现此函数。
        """
        raise NotImplementedError


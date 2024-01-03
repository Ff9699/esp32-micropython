"""
MIT License

Copyright (c) 2020-2023 Russ Hughes

Copyright (c) 2019 Ivan Belokobylskiy

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

The driver is based on devbis' st7789py_mpy module from
https://github.com/devbis/st7789py_mpy.

This driver supports:

- 320x240, 240x240, 135x240 and 128x128 pixel displays
- Display rotation
- RGB and BGR color orders
- Hardware based scrolling
- Drawing text using 8 and 16 bit wide bitmap fonts with heights that are
  multiples of 8.  Included are 12 bitmap fonts derived from classic pc
  BIOS text mode fonts.
- Drawing text using converted TrueType fonts.
- Drawing converted bitmaps
- Named color constants

  - BLACK
  - BLUE
  - RED
  - GREEN
  - CYAN
  - MAGENTA
  - YELLOW
  - WHITE

"""

from math import sin, cos

#
# 这允许sphinx构建文档
#

try:
    from time import sleep_ms
except ImportError:
    sleep_ms = lambda ms: None
    uint = int
    const = lambda x: x

    class micropython:
        @staticmethod
        def viper(func):
            return func

        @staticmethod
        def native(func):
            return func


#
# 如果你不需要构建文档，你可以删除
# 这里和上面注释之间的所有行，除了 "from time import sleep_ms" 这一行。
#

import struct

# ST7789 命令
_ST7789_SWRESET = b"\x01"
_ST7789_SLPIN = b"\x10"
_ST7789_SLPOUT = b"\x11"
_ST7789_NORON = b"\x13"
_ST7789_INVOFF = b"\x20"
_ST7789_INVON = b"\x21"
_ST7789_DISPOFF = b"\x28"
_ST7789_DISPON = b"\x29"
_ST7789_CASET = b"\x2a"
_ST7789_RASET = b"\x2b"
_ST7789_RAMWR = b"\x2c"
_ST7789_VSCRDEF = b"\x33"
_ST7789_COLMOD = b"\x3a"
_ST7789_MADCTL = b"\x36"
_ST7789_VSCSAD = b"\x37"
_ST7789_RAMCTL = b"\xb0"

# MADCTL 位
_ST7789_MADCTL_MY = const(0x80)
_ST7789_MADCTL_MX = const(0x40)
_ST7789_MADCTL_MV = const(0x20)
_ST7789_MADCTL_ML = const(0x10)
_ST7789_MADCTL_BGR = const(0x08)
_ST7789_MADCTL_MH = const(0x04)
_ST7789_MADCTL_RGB = const(0x00)

RGB = 0x00
BGR = 0x08

# 颜色模式
_COLOR_MODE_65K = const(0x50)
_COLOR_MODE_262K = const(0x60)
_COLOR_MODE_12BIT = const(0x03)
_COLOR_MODE_16BIT = const(0x05)
_COLOR_MODE_18BIT = const(0x06)
_COLOR_MODE_16M = const(0x07)

# 颜色定义
BLACK = const(0x0000)
BLUE = const(0x001F)
RED = const(0xF800)
GREEN = const(0x07E0)
CYAN = const(0x07FF)
MAGENTA = const(0xF81F)
YELLOW = const(0xFFE0)
WHITE = const(0xFFFF)

_ENCODE_PIXEL = const(">H")
_ENCODE_PIXEL_SWAPPED = const("<H")
_ENCODE_POS = const(">HH")
_ENCODE_POS_16 = const("<HH")

# 必须至少为128，用于8位宽字体
# 必须至少为256，用于16位宽字体
_BUFFER_SIZE = const(256)

_BIT7 = const(0x80)
_BIT6 = const(0x40)
_BIT5 = const(0x20)
_BIT4 = const(0x10)
_BIT3 = const(0x08)
_BIT2 = const(0x04)
_BIT1 = const(0x02)
_BIT0 = const(0x01)

# fmt: off

# 旋转表
#   (madctl, width, height, xstart, ystart, needs_swap)[rotation % 4]

_DISPLAY_240x320 = (
    (0x00, 240, 320, 0, 0, False),
    (0x60, 320, 240, 0, 0, False),
    (0xc0, 240, 320, 0, 0, False),
    (0xa0, 320, 240, 0, 0, False))

_DISPLAY_240x240 = (
    (0x00, 240, 240,  0,  0, False),
    (0x60, 240, 240,  0,  0, False),
    (0xc0, 240, 240,  0, 80, False),
    (0xa0, 240, 240, 80,  0, False))

_DISPLAY_135x240 = (
    (0x00, 135, 240, 52, 40, False),
    (0x60, 240, 135, 40, 53, False),
    (0xc0, 135, 240, 53, 40, False),
    (0xa0, 240, 135, 40, 52, False))

_DISPLAY_128x128 = (
    (0x00, 128, 128, 2, 1, False),
    (0x60, 128, 128, 1, 2, False),
    (0xc0, 128, 128, 2, 1, False),
    (0xa0, 128, 128, 1, 2, False))

# 旋转表的索引值
_WIDTH = const(0)
_HEIGHT = const(1)
_XSTART = const(2)
_YSTART = const(3)
_NEEDS_SWAP = const(4)

# 支持的显示器 (物理宽度, 物理高度, 旋转表)
_SUPPORTED_DISPLAYS = (
    (240, 320, _DISPLAY_240x320),
    (240, 240, _DISPLAY_240x240),
    (135, 240, _DISPLAY_135x240),
    (128, 128, _DISPLAY_128x128))

# 初始化元组格式 (b'command', b'data', delay_ms)
_ST7789_INIT_CMDS = (
    ( b'\x11', b'\x00', 120),               # 退出睡眠模式
    ( b'\x13', b'\x00', 0),                 # 打开显示器
    ( b'\xb6', b'\x0a\x82', 0),             # 设置显示功能控制
    ( b'\x3a', b'\x55', 10),                # 设置像素格式为每像素16位 (RGB565)
    ( b'\xb2', b'\x0c\x0c\x00\x33\x33', 0), # 设置门廊控制
    ( b'\xb7', b'\x35', 0),                 # 设置门控制
    ( b'\xbb', b'\x28', 0),                 # 设置VCOMS设置
    ( b'\xc0', b'\x0c', 0),                 # 设置电源控制1
    ( b'\xc2', b'\x01\xff', 0),             # 设置电源控制2
    ( b'\xc3', b'\x10', 0),                 # 设置电源控制3
    ( b'\xc4', b'\x20', 0),                 # 设置电源控制4
    ( b'\xc6', b'\x0f', 0),                 # 设置VCOM控制1
    ( b'\xd0', b'\xa4\xa1', 0),             # 设置电源控制A
                                            # 设置正极性伽马曲线
    ( b'\xe0', b'\xd0\x00\x02\x07\x0a\x28\x32\x44\x42\x06\x0e\x12\x14\x17', 0),
                                            # 设置负极性伽马曲线
    ( b'\xe1', b'\xd0\x00\x02\x07\x0a\x28\x31\x54\x47\x0e\x1c\x17\x1b\x1e', 0),
    ( b'\x21', b'\x00', 0),                 # 启用显示反转
    ( b'\x29', b'\x00', 120)                # 打开显示器
)

# fmt: on


def color565(red, green=0, blue=0):
    """
    将红、绿、蓝值（0-255）转换为16位565编码。
    """
    if isinstance(red, (tuple, list)):
        red, green, blue = red[:3]
    return (red & 0xF8) << 8 | (green & 0xFC) << 3 | blue >> 3


class ST7789:
    """
    ST7789驱动类

    参数:
        spi (spi): spi对象 **必需**
        width (int): 显示宽度 **必需**
        height (int): 显示高度 **必需**
        reset (pin): 重置引脚
        dc (pin): dc引脚 **必需**
        cs (pin): cs引脚
        backlight(pin): 背光引脚
        rotation (int):

          - 0-纵向
          - 1-横向
          - 2-反向纵向
          - 3-反向横向

        color_order (int):

          - RGB: 红色，绿色，蓝色，默认
          - BGR: 蓝色，绿色，红色

        custom_init (tuple): 自定义初始化命令

          - ((b'command', b'data', delay_ms), ...)

        custom_rotations (tuple): 自定义旋转定义

          - ((width, height, xstart, ystart, madctl, needs_swap), ...)

    """

    def __init__(
        self,
        spi,
        width,
        height,
        reset=None,
        dc=None,
        cs=None,
        backlight=None,
        rotation=0,
        color_order=BGR,
        custom_init=None,
        custom_rotations=None,
    ):
        """
        初始化显示。
        """
        self.rotations = custom_rotations or self._find_rotations(width, height)
        if not self.rotations:
            supported_displays = ", ".join(
                [f"{display[0]}x{display[1]}" for display in _SUPPORTED_DISPLAYS]
            )
            raise ValueError(
                f"不支持的 {width}x{height} 显示。支持的显示: {supported_displays}"
            )

        if dc is None:
            raise ValueError("dc引脚是必需的。")

        self.physical_width = self.width = width
        self.physical_height = self.height = height
        self.xstart = 0
        self.ystart = 0
        self.spi = spi
        self.reset = reset
        self.dc = dc
        self.cs = cs
        self.backlight = backlight
        self._rotation = rotation % 4
        self.color_order = color_order
        self.init_cmds = custom_init or _ST7789_INIT_CMDS
        self.hard_reset()
        # 是的，两次，一次通常不够
        self.init(self.init_cmds)
        self.init(self.init_cmds)
        self.rotation(self._rotation)
        self.needs_swap = False
        self.fill(0x0)

        if backlight is not None:
            backlight.value(1)

    @staticmethod
    def _find_rotations(width, height):
        for display in _SUPPORTED_DISPLAYS:
            if display[0] == width and display[1] == height:
                return display[2]
        return None

    def init(self, commands):
        """
        初始化显示。
        """
        for command, data, delay in commands:
            self._write(command, data)
            sleep_ms(delay)

    def _write(self, command=None, data=None):
        """SPI写入设备：命令和数据。"""
        if self.cs:
            self.cs.off()
        if command is not None:
            self.dc.off()
            self.spi.write(command)
        if data is not None:
            self.dc.on()
            self.spi.write(data)
            if self.cs:
                self.cs.on()

    def hard_reset(self):
        """
        对显示进行硬重置。
        """
        if self.cs:
            self.cs.off()
        if self.reset:
            self.reset.on()
        sleep_ms(10)
        if self.reset:
            self.reset.off()
        sleep_ms(10)
        if self.reset:
            self.reset.on()
        sleep_ms(120)
        if self.cs:
            self.cs.on()

    def soft_reset(self):
        """
        对显示进行软重置。
        """
        self._write(_ST7789_SWRESET)
        sleep_ms(150)

    def sleep_mode(self, value):
        """
        启用或禁用显示睡眠模式。

        参数:
            value (bool): 如果为True，则启用睡眠模式。如果为False，则禁用睡眠模式
        """
        if value:
            self._write(_ST7789_SLPIN)
        else:
            self._write(_ST7789_SLPOUT)

    def inversion_mode(self, value):
        """
        启用或禁用显示反转模式。

        参数:
            value (bool): 如果为True，则启用反转模式。如果为False，则禁用反转模式
        """
        if value:
            self._write(_ST7789_INVON)
        else:
            self._write(_ST7789_INVOFF)

    def rotation(self, rotation):
        """
        设置显示旋转。

        参数:
            rotation (int):
                - 0-纵向
                - 1-横向
                - 2-反向纵向
                - 3-反向横向

            custom_rotations可以有任意数量的旋转
        """
        rotation %= len(self.rotations)
        self._rotation = rotation
        (
            madctl,
            self.width,
            self.height,
            self.xstart,
            self.ystart,
            self.needs_swap,
        ) = self.rotations[rotation]

        if self.color_order == BGR:
            madctl |= _ST7789_MADCTL_BGR
        else:
            madctl &= ~_ST7789_MADCTL_BGR

        self._write(_ST7789_MADCTL, bytes([madctl]))

    def _set_window(self, x0, y0, x1, y1):
        """
        设置窗口到列和行地址。

        参数:
            x0 (int): 列开始地址
            y0 (int): 行开始地址
            x1 (int): 列结束地址
            y1 (int): 行结束地址
        """
        if x0 <= x1 <= self.width and y0 <= y1 <= self.height:
            self._write(
                _ST7789_CASET,
                struct.pack(_ENCODE_POS, x0 + self.xstart, x1 + self.xstart),
            )
            self._write(
                _ST7789_RASET,
                struct.pack(_ENCODE_POS, y0 + self.ystart, y1 + self.ystart),
            )
            self._write(_ST7789_RAMWR)

    def vline(self, x, y, length, color):
        """
        在给定的位置和颜色处绘制垂直线。

        参数:
            x (int): x坐标
            Y (int): y坐标
            length (int): 线的长度
            color (int): 565编码的颜色
        """
        self.fill_rect(x, y, 1, length, color)

    def hline(self, x, y, length, color):
        """
        在给定的位置和颜色处绘制水平线。

        参数:
            x (int): x坐标
            Y (int): y坐标
            length (int): 线的长度
            color (int): 565编码的颜色
        """
        self.fill_rect(x, y, length, 1, color)

    def pixel(self, x, y, color):
        """
        在给定的位置和颜色处绘制一个像素。

        参数:
            x (int): x坐标
            Y (int): y坐标
            color (int): 565编码的颜色
        """
        self._set_window(x, y, x, y)
        self._write(
            None,
            struct.pack(
                _ENCODE_PIXEL_SWAPPED if self.needs_swap else _ENCODE_PIXEL, color
            ),
        )

    def blit_buffer(self, buffer, x, y, width, height):
        """
        将缓冲区复制到给定位置的显示器上。

        参数:
            buffer (bytes): 要复制到显示器的数据
            x (int): 左上角x坐标
            Y (int): 左上角y坐标
            width (int): 宽度
            height (int): 高度
        """
        self._set_window(x, y, x + width - 1, y + height - 1)
        self._write(None, buffer)

    def rect(self, x, y, w, h, color):
        """
        在给定的位置、大小和颜色处绘制一个矩形。

        参数:
            x (int): 左上角x坐标
            y (int): 左上角y坐标
            width (int): 像素宽度
            height (int): 像素高度
            color (int): 565编码的颜色
        """
        self.hline(x, y, w, color)
        self.vline(x, y, h, color)
        self.vline(x + w - 1, y, h, color)
        self.hline(x, y + h - 1, w, color)

    def fill_rect(self, x, y, width, height, color):
        """
        在给定的位置、大小和颜色处绘制一个填充的矩形。

        参数:
            x (int): 左上角x坐标
            y (int): 左上角y坐标
            width (int): 像素宽度
            height (int): 像素高度
            color (int): 565编码的颜色
        """
        self._set_window(x, y, x + width - 1, y + height - 1)
        chunks, rest = divmod(width * height, _BUFFER_SIZE)
        pixel = struct.pack(
            _ENCODE_PIXEL_SWAPPED if self.needs_swap else _ENCODE_PIXEL, color
        )
        self.dc.on()
        if chunks:
            data = pixel * _BUFFER_SIZE
            for _ in range(chunks):
                self._write(None, data)
        if rest:
            self._write(None, pixel * rest)

    def fill(self, color):
        """
        用指定的颜色填充整个FrameBuffer。

        参数:
            color (int): 565编码的颜色
        """
        self.fill_rect(0, 0, self.width, self.height, color)

    def line(self, x0, y0, x1, y1, color):
        """
        从x0, y0开始，到x1, y1结束，绘制一条单像素宽的线。

        参数:
            x0 (int): 起点x坐标
            y0 (int): 起点y坐标
            x1 (int): 终点x坐标
            y1 (int): 终点y坐标
            color (int): 565编码的颜色
        """
        steep = abs(y1 - y0) > abs(x1 - x0)
        if steep:
            x0, y0 = y0, x0
            x1, y1 = y1, x1
        if x0 > x1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0
        dx = x1 - x0
        dy = abs(y1 - y0)
        err = dx // 2
        ystep = 1 if y0 < y1 else -1
        while x0 <= x1:
            if steep:
                self.pixel(y0, x0, color)
            else:
                self.pixel(x0, y0, color)
            err -= dy
            if err < 0:
                y0 += ystep
                err += dx
            x0 += 1

    def vscrdef(self, tfa, vsa, bfa):
        """
        设置垂直滚动定义。

        要滚动135x240的显示器，这些值应为40, 240, 40。
        显示器上方有40行不显示，然后显示240行，然后再有40行不显示。
        您可以写入这些显示区域外的区域，并通过更改TFA、VSA和BFA值将它们滚动到视图中。

        参数:
            tfa (int): 顶部固定区域
            vsa (int): 垂直滚动区域
            bfa (int): 底部固定区域
        """
        self._write(_ST7789_VSCRDEF, struct.pack(">HHH", tfa, vsa, bfa))

    def vscsad(self, vssa):
        """
        设置RAM的垂直滚动开始地址。

        定义在显示器上的顶部固定区域的最后一行之后将作为第一行写入的帧存储器中的哪一行

        示例:

            for line in range(40, 280, 1):
                tft.vscsad(line)
                utime.sleep(0.01)

        参数:
            vssa (int): 垂直滚动开始地址

        """
        self._write(_ST7789_VSCSAD, struct.pack(">H", vssa))

    @micropython.viper
    @staticmethod
    def _pack8(glyphs, idx: uint, fg_color: uint, bg_color: uint):
        buffer = bytearray(128)
        bitmap = ptr16(buffer)
        glyph = ptr8(glyphs)

        for i in range(0, 64, 8):
            byte = glyph[idx]
            bitmap[i] = fg_color if byte & _BIT7 else bg_color
            bitmap[i + 1] = fg_color if byte & _BIT6 else bg_color
            bitmap[i + 2] = fg_color if byte & _BIT5 else bg_color
            bitmap[i + 3] = fg_color if byte & _BIT4 else bg_color
            bitmap[i + 4] = fg_color if byte & _BIT3 else bg_color
            bitmap[i + 5] = fg_color if byte & _BIT2 else bg_color
            bitmap[i + 6] = fg_color if byte & _BIT1 else bg_color
            bitmap[i + 7] = fg_color if byte & _BIT0 else bg_color
            idx += 1

        return buffer

    @micropython.viper
    @staticmethod
    def _pack16(glyphs, idx: uint, fg_color: uint, bg_color: uint):
        """
        将一个字符打包成一个字节数组。

        参数:
            char (str): 要打包的字符

        返回:
            128字节: color565格式的字符位图
        """

        buffer = bytearray(256)
        bitmap = ptr16(buffer)
        glyph = ptr8(glyphs)

        for i in range(0, 128, 16):
            byte = glyph[idx]

            bitmap[i] = fg_color if byte & _BIT7 else bg_color
            bitmap[i + 1] = fg_color if byte & _BIT6 else bg_color
            bitmap[i + 2] = fg_color if byte & _BIT5 else bg_color
            bitmap[i + 3] = fg_color if byte & _BIT4 else bg_color
            bitmap[i + 4] = fg_color if byte & _BIT3 else bg_color
            bitmap[i + 5] = fg_color if byte & _BIT2 else bg_color
            bitmap[i + 6] = fg_color if byte & _BIT1 else bg_color
            bitmap[i + 7] = fg_color if byte & _BIT0 else bg_color
            idx += 1

            byte = glyph[idx]
            bitmap[i + 8] = fg_color if byte & _BIT7 else bg_color
            bitmap[i + 9] = fg_color if byte & _BIT6 else bg_color
            bitmap[i + 10] = fg_color if byte & _BIT5 else bg_color
            bitmap[i + 11] = fg_color if byte & _BIT4 else bg_color
            bitmap[i + 12] = fg_color if byte & _BIT3 else bg_color
            bitmap[i + 13] = fg_color if byte & _BIT2 else bg_color
            bitmap[i + 14] = fg_color if byte & _BIT1 else bg_color
            bitmap[i + 15] = fg_color if byte & _BIT0 else bg_color
            idx += 1

        return buffer

    def _text8(self, font, text, x0, y0, fg_color=WHITE, bg_color=BLACK):
        """
        内部方法，用于写入宽度为8，高度为8或16的字符。

        参数:
            font (module): 要使用的字体模块
            text (str): 要写入的文本
            x0 (int): 开始绘制的列
            y0 (int): 开始绘制的行
            color (int): 用于字符的565编码颜色
            background (int): 用于背景的565编码颜色
        """

        for char in text:
            ch = ord(char)
            if (
                font.FIRST <= ch < font.LAST
                and x0 + font.WIDTH <= self.width
                and y0 + font.HEIGHT <= self.height
            ):
                if font.HEIGHT == 8:
                    passes = 1
                    size = 8
                    each = 0
                else:
                    passes = 2
                    size = 16
                    each = 8

                for line in range(passes):
                    idx = (ch - font.FIRST) * size + (each * line)
                    buffer = self._pack8(font.FONT, idx, fg_color, bg_color)
                    self.blit_buffer(buffer, x0, y0 + 8 * line, 8, 8)

                x0 += 8

    def _text16(self, font, text, x0, y0, fg_color=WHITE, bg_color=BLACK):
        """
        内部方法，用于绘制宽度为16，高度为16或32的字符。

        参数:
            font (module): 要使用的字体模块
            text (str): 要写入的文本
            x0 (int): 开始绘制的列
            y0 (int): 开始绘制的行
            color (int): 用于字符的565编码颜色
            background (int): 用于背景的565编码颜色
        """

        for char in text:
            ch = ord(char)
            if (
                font.FIRST <= ch < font.LAST
                and x0 + font.WIDTH <= self.width
                and y0 + font.HEIGHT <= self.height
            ):
                each = 16
                if font.HEIGHT == 16:
                    passes = 2
                    size = 32
                else:
                    passes = 4
                    size = 64

                for line in range(passes):
                    idx = (ch - font.FIRST) * size + (each * line)
                    buffer = self._pack16(font.FONT, idx, fg_color, bg_color)
                    self.blit_buffer(buffer, x0, y0 + 8 * line, 16, 8)
            x0 += 16

    def text(self, font, text, x0, y0, color=WHITE, background=BLACK):
        """
        在指定的字体和颜色上绘制文本。支持8和16位宽的字体。

        参数:
            font (module): 要使用的字体模块。
            text (str): 要写入的文本
            x0 (int): 开始绘制的列
            y0 (int): 开始绘制的行
            color (int): 用于字符的565编码颜色
            background (int): 用于背景的565编码颜色
        """
        fg_color = color if self.needs_swap else ((color << 8) & 0xFF00) | (color >> 8)
        bg_color = (
            background
            if self.needs_swap
            else ((background << 8) & 0xFF00) | (background >> 8)
        )

        if font.WIDTH == 8:
            self._text8(font, text, x0, y0, fg_color, bg_color)
        else:
            self._text16(font, text, x0, y0, fg_color, bg_color)

    def bitmap(self, bitmap, x, y, index=0):
        """
        在指定的列和行上显示位图

        参数:
            bitmap (bitmap_module): 包含要绘制的位图的模块
            x (int): 开始绘制的列
            y (int): 开始绘制的行
            index (int): 可选的位图索引，从多个位图模块中绘制
        """
        width = bitmap.WIDTH
        height = bitmap.HEIGHT
        to_col = x + width - 1
        to_row = y + height - 1
        if self.width <= to_col or self.height <= to_row:
            return

        bitmap_size = height * width
        buffer_len = bitmap_size * 2
        bpp = bitmap.BPP
        bs_bit = bpp * bitmap_size * index  # if index > 0 else 0
        palette = bitmap.PALETTE
        needs_swap = self.needs_swap
        buffer = bytearray(buffer_len)

        for i in range(0, buffer_len, 2):
            color_index = 0
            for _ in range(bpp):
                color_index = (color_index << 1) | (
                    (bitmap.BITMAP[bs_bit >> 3] >> (7 - (bs_bit & 7))) & 1
                )
                bs_bit += 1

            color = palette[color_index]
            if needs_swap:
                buffer[i] = color & 0xFF
                buffer[i + 1] = color >> 8
            else:
                buffer[i] = color >> 8
                buffer[i + 1] = color & 0xFF

        self._set_window(x, y, to_col, to_row)
        self._write(None, buffer)

    def pbitmap(self, bitmap, x, y, index=0):
        """
        在指定的列和行上一行一行地显示位图

        参数:
            bitmap (bitmap_module): 包含要绘制的位图的模块
            x (int): 开始绘制的列
            y (int): 开始绘制的行
            index (int): 可选的位图索引，从多个位图模块中绘制

        """
        width = bitmap.WIDTH
        height = bitmap.HEIGHT
        bitmap_size = height * width
        bpp = bitmap.BPP
        bs_bit = bpp * bitmap_size * index  # if index > 0 else 0
        palette = bitmap.PALETTE
        needs_swap = self.needs_swap
        buffer = bytearray(bitmap.WIDTH * 2)

        for row in range(height):
            for col in range(width):
                color_index = 0
                for _ in range(bpp):
                    color_index <<= 1
                    color_index |= (
                        bitmap.BITMAP[bs_bit // 8] & 1 << (7 - (bs_bit % 8))
                    ) > 0
                    bs_bit += 1
                color = palette[color_index]
                if needs_swap:
                    buffer[col * 2] = color & 0xFF
                    buffer[col * 2 + 1] = color >> 8 & 0xFF
                else:
                    buffer[col * 2] = color >> 8 & 0xFF
                    buffer[col * 2 + 1] = color & 0xFF

            to_col = x + width - 1
            to_row = y + row
            if self.width > to_col and self.height > to_row:
                self._set_window(x, y + row, to_col, to_row)
                self._write(None, buffer)

    def write(self, font, string, x, y, fg=WHITE, bg=BLACK):
        """
        使用转换后的真实类型字体在指定的列和行上写入字符串

        参数:
            font (font): 包含转换后的真实类型字体的模块
            s (string): 要写入的字符串
            x (int): 开始写入的列
            y (int): 开始写入的行
            fg (int): 前景色，可选，默认为白色
            bg (int): 背景色，可选，默认为黑色
        """
        buffer_len = font.HEIGHT * font.MAX_WIDTH * 2
        buffer = bytearray(buffer_len)
        fg_hi = fg >> 8
        fg_lo = fg & 0xFF

        bg_hi = bg >> 8
        bg_lo = bg & 0xFF

        for character in string:
            try:
                char_index = font.MAP.index(character)
                offset = char_index * font.OFFSET_WIDTH
                bs_bit = font.OFFSETS[offset]
                if font.OFFSET_WIDTH > 1:
                    bs_bit = (bs_bit << 8) + font.OFFSETS[offset + 1]

                if font.OFFSET_WIDTH > 2:
                    bs_bit = (bs_bit << 8) + font.OFFSETS[offset + 2]

                char_width = font.WIDTHS[char_index]
                buffer_needed = char_width * font.HEIGHT * 2

                for i in range(0, buffer_needed, 2):
                    if font.BITMAPS[bs_bit // 8] & 1 << (7 - (bs_bit % 8)) > 0:
                        buffer[i] = fg_hi
                        buffer[i + 1] = fg_lo
                    else:
                        buffer[i] = bg_hi
                        buffer[i + 1] = bg_lo

                    bs_bit += 1

                to_col = x + char_width - 1
                to_row = y + font.HEIGHT - 1
                if self.width > to_col and self.height > to_row:
                    self._set_window(x, y, to_col, to_row)
                    self._write(None, buffer[:buffer_needed])

                x += char_width

            except ValueError:
                pass

    def write_width(self, font, string):
        """
        如果使用指定的字体写入，返回字符串的像素宽度

        参数:
            font (font): 包含转换后的真实类型字体的模块
            string (string): 要测量的字符串

        返回:
            int: 字符串的像素宽度

        """
        width = 0
        for character in string:
            try:
                char_index = font.MAP.index(character)
                width += font.WIDTHS[char_index]
            except ValueError:
                pass

        return width

    @micropython.native
    def polygon(self, points, x, y, color, angle=0, center_x=0, center_y=0):
        """
        在显示器上绘制一个多边形。

        参数:
            points (list): 要绘制的点的列表。
            x (int): 多边形位置的X坐标。
            y (int): 多边形位置的Y坐标。
            color (int): 565编码颜色。
            angle (float): 旋转角度，以弧度为单位（默认：0）。
            center_x (int): 旋转中心的X坐标（默认：0）。
            center_y (int): 旋转中心的Y坐标（默认：0）。

        引发:
            ValueError: 如果多边形少于3个点。
        """
        if len(points) < 3:
            raise ValueError("多边形必须至少有3个点。")

        if angle:
            cos_a = cos(angle)
            sin_a = sin(angle)
            rotated = [
                (
                    x
                    + center_x
                    + int(
                        (point[0] - center_x) * cos_a - (point[1] - center_y) * sin_a
                    ),
                    y
                    + center_y
                    + int(
                        (point[0] - center_x) * sin_a + (point[1] - center_y) * cos_a
                    ),
                )
                for point in points
            ]
        else:
            rotated = [(x + int((point[0])), y + int((point[1]))) for point in points]

        for i in range(1, len(rotated)):
            self.line(
                rotated[i - 1][0],
                rotated[i - 1][1],
                rotated[i][0],
                rotated[i][1],
                color,
            )



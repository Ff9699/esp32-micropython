# SPDX-FileCopyrightText: 2017 Michael McWethy for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
`adafruit_ssd1306`
====================================================

MicroPython SSD1306 OLED驱动程序，I2C和SPI接口

* 作者: Tony DiCola, Michael McWethy
"""

import time

from micropython import const
from adafruit_bus_device import i2c_device, spi_device

try:
    # 导入MicroPython framebuf
    import framebuf

    _FRAMEBUF_FORMAT = framebuf.MONO_VLSB
except ImportError:
    # 导入CircuitPython framebuf
    import adafruit_framebuf as framebuf

    _FRAMEBUF_FORMAT = framebuf.MVLSB

try:
    # 仅用于类型检查
    from typing import Optional
    import busio
    import digitalio
except ImportError:
    pass

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_SSD1306.git"

# 寄存器定义
SET_CONTRAST = const(0x81)
SET_ENTIRE_ON = const(0xA4)
SET_NORM_INV = const(0xA6)
SET_DISP = const(0xAE)
SET_MEM_ADDR = const(0x20)
SET_COL_ADDR = const(0x21)
SET_PAGE_ADDR = const(0x22)
SET_DISP_START_LINE = const(0x40)
SET_SEG_REMAP = const(0xA0)
SET_MUX_RATIO = const(0xA8)
SET_IREF_SELECT = const(0xAD)
SET_COM_OUT_DIR = const(0xC0)
SET_DISP_OFFSET = const(0xD3)
SET_COM_PIN_CFG = const(0xDA)
SET_DISP_CLK_DIV = const(0xD5)
SET_PRECHARGE = const(0xD9)
SET_VCOM_DESEL = const(0xDB)
SET_CHARGE_PUMP = const(0x8D)

class _SSD1306(framebuf.FrameBuffer):
    """SSD1306 显示驱动的基类"""

    # pylint: disable-msg=too-many-arguments
    def __init__(
        self,
        buffer: memoryview,
        width: int,
        height: int,
        *,
        external_vcc: bool,
        reset: Optional[digitalio.DigitalInOut],
        page_addressing: bool
    ):
        super().__init__(buffer, width, height, _FRAMEBUF_FORMAT)
        self.width = width
        self.height = height
        self.external_vcc = external_vcc
        # 如果不需要重置，则重置可能为 None
        self.reset_pin = reset
        self.page_addressing = page_addressing
        if self.reset_pin:
            self.reset_pin.switch_to_output(value=0)
        self.pages = self.height // 8
        # 注意：子类必须将 self.framebuf 初始化为 framebuffer。
        # 这是必要的，因为 I2C 和 SPI 实现之间的数据缓冲区不同（I2C 需要额外的字节）。
        self._power = False
        # 用于高效的页面寻址模式参数（U8Glib 库的典型特性）
        # 重要，因为似乎并非所有屏幕都支持水平寻址模式
        if self.page_addressing:
            self.pagebuffer = bytearray(width + 1)  # type: Optional[bytearray]
            self.pagebuffer[0] = 0x40  # 将数据缓冲区的第一个字节设置为 Co=0, D/C=1
            self.page_column_start = bytearray(2)  # type: Optional[bytearray]
            self.page_column_start[0] = self.width % 32
            self.page_column_start[1] = 0x10 + self.width // 32
        else:
            self.pagebuffer = None
            self.page_column_start = None
        # 让我们开始吧！
        self.poweron()
        self.init_display()

    @property
    def power(self) -> bool:
        """如果显示当前已经开启，则为 True，否则为 False"""
        return self._power

    def init_display(self) -> None:
        """初始化显示的基类"""
        # ssd1306 OLED 驱动芯片提供的各种屏幕尺寸
        # 需要不同的显示时钟分频和 com 引脚配置值，以下是供参考和未来兼容性的列表：
        #    w,  h: DISP_CLK_DIV  COM_PIN_CFG
        #  128, 64:         0x80         0x12
        #  128, 32:         0x80         0x02
        #   96, 16:         0x60         0x02
        #   64, 48:         0x80         0x12
        #   64, 32:         0x80         0x12
        for cmd in (
            SET_DISP,  # 关闭
            # 地址设置
            SET_MEM_ADDR,
            0x10  # 页面寻址模式
            if self.page_addressing
            else 0x00,  # 水平寻址模式
            # 分辨率和布局
            SET_DISP_START_LINE,
            SET_SEG_REMAP | 0x01,  # 列地址 127 映射到 SEG0
            SET_MUX_RATIO,
            self.height - 1,
            SET_COM_OUT_DIR | 0x08,  # 从 COM[N] 到 COM0 扫描
            SET_DISP_OFFSET,
            0x00,
            SET_COM_PIN_CFG,
            0x02 if self.width > 2 * self.height else 0x12,
            # 时序和驱动方案
            SET_DISP_CLK_DIV,
            0x80,
            SET_PRECHARGE,
            0x22 if self.external_vcc else 0xF1,
            SET_VCOM_DESEL,
            0x30,  # 0.83*Vcc  # 注意：ssd1306 64x32 oled 屏幕的规格暗示这应该是 0x40
            # 显示
            SET_CONTRAST,
            0xFF,  # 最大
            SET_ENTIRE_ON,  # 输出跟随 RAM 内容
            SET_NORM_INV,  # 非反转
            SET_IREF_SELECT,
            0x30,  # 在显示开启时启用内部 IREF
            # 充电泵
            SET_CHARGE_PUMP,
            0x10 if self.external_vcc else 0x14,
            SET_DISP | 0x01,  # 显示开启
        ):
            self.write_cmd(cmd)
        self.fill(0)
        self.show()

    def poweroff(self) -> None:
        """关闭显示（无内容可见）"""
        self.write_cmd(SET_DISP)
        self._power = False

    def contrast(self, contrast: int) -> None:
        """调整对比度"""
        self.write_cmd(SET_CONTRAST)
        self.write_cmd(contrast)

    def invert(self, invert: bool) -> None:
        """反转显示中的所有像素"""
        self.write_cmd(SET_NORM_INV | (invert & 1))

    def rotate(self, rotate: bool) -> None:
        """将显示旋转 0 或 180 度"""
        self.write_cmd(SET_COM_OUT_DIR | ((rotate & 1) << 3))
        self.write_cmd(SET_SEG_REMAP | (rotate & 1))
        # com 输出（垂直镜像）立即更改
        # 需要调用 show() 才能看到 seg remap

    def write_framebuf(self) -> None:
        """派生类必须实现此方法"""
        raise NotImplementedError

    def write_cmd(self, cmd: int) -> None:
        """派生类必须实现此方法"""
        raise NotImplementedError

    def poweron(self) -> None:
        "重置设备并打开显示。"
        if self.reset_pin:
            self.reset_pin.value = 1
            time.sleep(0.001)
            self.reset_pin.value = 0
            time.sleep(0.010)
            self.reset_pin.value = 1
            time.sleep(0.010)
        self.write_cmd(SET_DISP | 0x01)
        self._power = True

    def show(self) -> None:
        """更新显示"""
        if not self.page_addressing:
            xpos0 = 0
            xpos1 = self.width - 1
            if self.width != 128:
                # 窄屏使用居中列
                col_offset = (128 - self.width) // 2
                xpos0 += col_offset
                xpos1 += col_offset
            self.write_cmd(SET_COL_ADDR)
            self.write_cmd(xpos0)
            self.write_cmd(xpos1)
            self.write_cmd(SET_PAGE_ADDR)
            self.write_cmd(0)
            self.write_cmd(self.pages - 1)
        self.write_framebuf()


class SSD1306_I2C(_SSD1306):
    """
    SSD1306的I2C类

    :param width: 屏幕的物理宽度（像素）,
    :param height: 屏幕的物理高度（像素）,
    :param i2c: 要使用的I2C外设,
    :param addr: 设备的8位总线地址,
    :param external_vcc: 是否连接外部高压源.
    :param reset: 如果需要，指定复位引脚的DigitalInOut
    """

    def __init__(
        self,
        width: int,
        height: int,
        i2c: busio.I2C,
        *,
        addr: int = 0x3C,
        external_vcc: bool = False,
        reset: Optional[digitalio.DigitalInOut] = None,
        page_addressing: bool = False
    ):
        self.i2c_device = i2c_device.I2CDevice(i2c, addr)
        self.addr = addr
        self.page_addressing = page_addressing
        self.temp = bytearray(2)
        # 添加一个额外的字节到数据缓冲区，用于保存I2C数据/命令字节，以支持硬件兼容的I2C事务。使用缓冲区的memoryview将此字节屏蔽在framebuffer操作中（由于memoryview不会复制到单独的缓冲区，因此不会有主要的内存开销）。
        self.buffer = bytearray(((height // 8) * width) + 1)
        self.buffer[0] = 0x40  # 将数据缓冲区的第一个字节设置为Co=0, D/C=1
        super().__init__(
            memoryview(self.buffer)[1:],
            width,
            height,
            external_vcc=external_vcc,
            reset=reset,
            page_addressing=self.page_addressing,
        )

    def write_cmd(self, cmd: int) -> None:
        """向I2C设备发送命令"""
        self.temp[0] = 0x80  # Co=1, D/C#=0
        self.temp[1] = cmd
        with self.i2c_device:
            self.i2c_device.write(self.temp)

    def write_framebuf(self) -> None:
        """使用单个I2C事务快速传输frame buffer以支持硬件I2C接口。"""
        if self.page_addressing:
            for page in range(self.pages):
                self.write_cmd(0xB0 + page)
                self.write_cmd(self.page_column_start[0])
                self.write_cmd(self.page_column_start[1])
                self.pagebuffer[1:] = self.buffer[
                    1 + self.width * page : 1 + self.width * (page + 1)
                ]
                with self.i2c_device:
                    self.i2c_device.write(self.pagebuffer)
        else:
            with self.i2c_device:
                self.i2c_device.write(self.buffer)

    # pylint: disable-msg=too-many-arguments
class SSD1306_SPI(_SSD1306):
    """
    SSD1306的SPI类

    :param width: 屏幕的物理宽度（像素）,
    :param height: 屏幕的物理高度（像素）,
    :param spi: 要使用的SPI外设,
    :param dc: 要使用的数据/命令引脚（通常标记为“D/C”）,
    :param reset: 要使用的复位引脚,
    :param cs: 要使用的片选引脚（有时标记为“SS”）。
    """

    # pylint: disable=no-member
    # 在重构可以测试时应重新考虑禁用。
    def __init__(
        self,
        width: int,
        height: int,
        spi: busio.SPI,
        dc: digitalio.DigitalInOut,
        reset: Optional[digitalio.DigitalInOut],
        cs: digitalio.DigitalInOut,
        *,
        external_vcc: bool = False,
        baudrate: int = 8000000,
        polarity: int = 0,
        phase: int = 0,
        page_addressing: bool = False
    ):
        self.page_addressing = page_addressing
        if self.page_addressing:
            raise NotImplementedError(
                "尚未实现SPI的页面寻址模式。"
            )

        self.rate = 10 * 1024 * 1024
        dc.switch_to_output(value=0)
        self.spi_device = spi_device.SPIDevice(
            spi, cs, baudrate=baudrate, polarity=polarity, phase=phase
        )
        self.dc_pin = dc
        self.buffer = bytearray((height // 8) * width)
        super().__init__(
            memoryview(self.buffer),
            width,
            height,
            external_vcc=external_vcc,
            reset=reset,
            page_addressing=self.page_addressing,
        )

    def write_cmd(self, cmd: int) -> None:
        """向SPI设备发送命令"""
        self.dc_pin.value = 0
        with self.spi_device as spi:
            spi.write(bytearray([cmd]))

    def write_framebuf(self) -> None:
        """通过SPI向帧缓冲区写入数据"""
        self.dc_pin.value = 1
        with self.spi_device as spi:
            spi.write(self.buffer)


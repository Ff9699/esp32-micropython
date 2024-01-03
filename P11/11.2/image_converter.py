#!/usr/bin/env python3
"""
将图像文件转换为可与位图方法一起使用的python模块。使用重定向将输出保存到文件。图像被转换为位图，使用您指定的每像素位数。
位图被保存为可以导入并与位图方法一起使用的python模块。

.. 参见::
    - :ref:`alien.py<alien>`.

示例
^^^^^^^

.. 代码块:: 控制台

    ./create_png_examples.py cat.png 4 > cat_bitmap.py

可以导入python文件并使用位图方法显示。例如：

.. 代码块:: python

    import tft_config
    import cat_bitmap
    tft = tft_config.config(1)
    tft.bitmap(cat_bitmap, 0, 0)

使用方法
^^^^^

.. 代码块:: 控制台

    使用方法: image_converter.py [-h] image_file bits_per_pixel

    将图像文件转换为可与位图方法一起使用的python模块。

    定位参数: image_file      包含要转换的图像的文件名 bits_per_pixel
    每像素使用的位数（1..8）

    可选参数: -h, --help      显示此帮助消息并退出

"""

import sys
import argparse
from PIL import Image


def rgb_to_color565(r, g, b):
    """
    将RGB颜色转换为16位颜色格式（565）。

    参数:
        r (int): RGB颜色的红色组件（0-255）。
        g (int): RGB颜色的绿色组件（0-255）。
        b (int): RGB颜色的蓝色组件（0-255）。

    返回:
        int: 转换后的颜色值，以16位颜色格式（565）。
    """

    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b & 0xF8)


def convert_to_bitmap(image_file, bits_requested):
    """
    将图像文件转换为可与位图方法一起使用的python模块。

    参数:
        image_file (str): 包含要转换的图像的文件名。
        bits (int): 每像素使用的位数（1..8）。
    """

    colors_requested = 1 << bits_requested
    img = Image.open(image_file).convert("RGB")
    img = img.convert("P", palette=Image.Palette.ADAPTIVE, colors=colors_requested)
    palette = img.getpalette()
    palette_colors = len(palette) // 3
    actual_colors = min(palette_colors, colors_requested)
    bits_required = actual_colors.bit_length()
    if bits_required < bits_requested:
        print(
            f"\n注意: 量化将颜色从请求的 {bits_requested} 减少到 {palette_colors}，"
            f"使用每像素 {bits_required} 位重新转换可以节省内存。\n",
            file=sys.stderr,
        )

    colors = [
        f"{rgb_to_color565(palette[color * 3], palette[color * 3 + 1], palette[color * 3 + 2]):04x}"
        for color in range(actual_colors)
    ]

    image_bitstring = "".join(
        "".join(
            "1" if (img.getpixel((x, y)) & (1 << bit - 1)) else "0"
            for bit in range(bits_required, 0, -1)
        )
        for y in range(img.height)
        for x in range(img.width)
    )

    bitmap_bits = len(image_bitstring)

    print(f"HEIGHT = {img.height}")
    print(f"WIDTH = {img.width}")
    print(f"COLORS = {actual_colors}")
    print(f"BITS = {bitmap_bits}")
    print(f"BPP = {bits_required}")
    print("PALETTE = [", end="")

    for i, rgb in enumerate(colors):
        if i > 0:
            print(",", end="")
        print(f"0x{rgb}", end="")

    print("]")

    print("_bitmap =\\\nb'", end="")

    for i in range(0, bitmap_bits, 8):
        if i and i % (16 * 8) == 0:
            print("'\\\nb'", end="")
        value = image_bitstring[i : i + 8]
        color = int(value, 2)
        print(f"\\x{color:02x}", end="")

    print("'\nBITMAP = memoryview(_bitmap)")


def main():
    """
    将图像文件转换为可与位图方法一起使用的python模块。

    参数:
        image_file (str): 包含要转换的图像的文件名。
        bits_per_pixel (int): 每像素使用的位数（1..8）。
    """

    parser = argparse.ArgumentParser(
        description="将图像文件转换为可与位图方法一起使用的python模块。",
    )

    parser.add_argument("image_file", help="包含要转换的图像的文件名")

    parser.add_argument(
        "bits_per_pixel",
        type=int,
        choices=range(1, 9),
        default=1,
        metavar="bits_per_pixel",
        help="每像素使用的位数（1..8）",
    )

    args = parser.parse_args()
    bits = args.bits_per_pixel
    convert_to_bitmap(args.image_file, bits)


if __name__ == "__main__":
    #main()
    convert_to_bitmap("alien.png", 1)
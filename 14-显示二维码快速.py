from uQR import QRCode
from machine import Pin, SPI
import st7789_itprojects


tft = st7789_itprojects.ST7889_Image(SPI(2, 60000000), dc=Pin(4), cs=Pin(5), rst=Pin(15))
tft.fill(st7789_itprojects.color565(255, 255, 255))  # 背景设置为白色


qr = QRCode(border=2)
qr.add_data('你好')
matrix = qr.get_matrix()

row_len = len(matrix)
col_len = len(matrix[0])

print("row=%d, col=%d" % (row_len, col_len))

# 放大倍数
scale_rate = 8

# 准备黑色，白色数据
'''
buffer_black = bytearray(scale_rate * scale_rate * 2)  # 创建byte列表，每个点pixel有2个字节表示颜色
buffer_white = bytearray(scale_rate * scale_rate * 2)  # 创建byte列表，每个点pixel有2个字节表示颜色
print(buffer_black,"\n",buffer_white)
color_black = st7789_itprojects.color565(0, 0, 0)
color_black_byte1 = color_black & 0xff00 >> 8    #高位
color_black_byte2 = color_black & 0xff           #低位
print(color_black_byte1,color_black_byte2)
color_white = st7789_itprojects.color565(255, 255, 255)
color_white_byte1 = color_white & 0xff00 >> 8
color_white_byte2 = color_white & 0xff

for i in range(0, scale_rate * scale_rate * 2, 2):
    buffer_black[i] = color_black_byte1
    buffer_black[i + 1] = color_black_byte2
    buffer_white[i] = color_white_byte1
    buffer_white[i + 1] = color_white_byte2
'''
buffer_black=bytearray([0x00]*scale_rate * scale_rate * 2) #创建8*8*2列表并填充0x00
buffer_white=bytearray([0xff]*scale_rate * scale_rate * 2)

print(buffer_black,"\n",buffer_white)
# 循环次数不增加，只增加每次发送的数据量，每次发送scale_rate X scale_rate个点的信息
for row in range(row_len):
    for col in range(col_len):
        if matrix[row][col]:
            # tft.pixel(row, col, st7789_itprojects.color565(0, 0, 0))
            tft.show_img(row * scale_rate, col * scale_rate, row * scale_rate + scale_rate - 1, col * scale_rate + scale_rate - 1, buffer_black)
        else:
            # tft.pixel(row, col, st7789_itprojects.color565(255, 255, 255))
            tft.show_img(row * scale_rate, col * scale_rate, row * scale_rate + scale_rate - 1 , col * scale_rate + scale_rate - 1, buffer_white)
        col += 1

    row += 1


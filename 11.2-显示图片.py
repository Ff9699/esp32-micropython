import time
import st7789py as st7789
import tft_config
import alien_bitmap as alien
import map48x as map48x
import map64x as map64x
import map128x as map128x
import test1 as test1

tft = tft_config.config(tft_config.WIDE)

def show_img1():
    '''
    读取位图"test1.py"，并显示在屏幕上。逐行pbitmap效率比较慢，逐行显示使用show_img2。
    '''
    #tft.fill_rect(last_col, old_row, alien.WIDTH, alien.HEIGHT, 0)
    #tft.bitmap(map48x, 0, 0)
    #tft.bitmap(map64x, 60, 0)
    #tft.bitmap(map128x, 190, 0)
    tft.pbitmap(test1, 0, 0)     #图片太大，超出内存，使用逐行扫描。
    
    
def show_img2():
    '''
    读取二进制图片"text_img.dat"，逐行显示在屏幕上。
    '''
    with open("text_img.dat", "rb") as f:
        for row in range(240):
            buffer = f.read(480)
            tft.blit_buffer(buffer,0,row,0,row)
    
show_img2()
time.sleep(5)
show_img1()
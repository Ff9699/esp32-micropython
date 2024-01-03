'''
i2s只能播放未压缩的音频（如wav格式），不能播放压缩过的音频（如mp3）。使用aconvert.com/cn/audio/网站转码。
'''
from machine import I2S
from machine import Pin
import urequests
import network
import time 

"""
GPIO12    --- BCLK
GPIO14    --- LRC
GPIO13    --- DIN
GND       --> GND
5V        --> VCC 
"""

# 初始化I2S引脚定义 
sck_pin = Pin(12)  # 串行时钟输出引脚 
ws_pin = Pin(14)   # 左/右声道选择 
sd_pin = Pin(13)   # 串行数据输出引脚 

"""
sck     串行时钟输出的引脚对象实例 
ws      左/右声道选择的引脚对象实例 
sd      串行数据输出的引脚对象实例 
mode    指定I2S收发模式  
bits    指定样本大小（位），16 或 32  
format  指定音频格式，STEREO（左右声道）或 MONO（单声道）  
rate    指定音频采样率（样本/秒）  
ibuf    指定内部缓冲区长度（字节）
"""

#初始化i2s
audio_out = I2S(
    1,
    sck=sck_pin,
    ws=ws_pin,
    sd=sd_pin,
    mode=I2S.TX,
    bits=16,            #采样位数16/32
    format=I2S.STEREO,  #单通道：I2S.MONO；双通道：I2S.STEREO
    rate=22050,         #设置为音频采样率
    ibuf=20000)


# 连接WIFI
def do_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect('wifi帐号', 'PASSWORD')
        i = 1
        while not wlan.isconnected():
            print(f"正在连接...{i}")
            i+=1
            time.sleep(1)
    print('network config:', wlan.ifconfig())

# 连接网络
do_connect()

# 上传至云端https,需要http
# 超级玛丽 http://doc.itprojects.cn/0006.zhishi.esp32/01.download/audio/chaojimaili.wav
response = urequests.get('http://doc.itprojects.cn/0006.zhishi.esp32/01.download/audio/maifu.wav', stream=True)
response.raw.read(44) # 跳过44字节的文件头，直接读取音频数据

print("开始播放音乐...")


# 用来读取音频 I2S DAC
while True:
    try:
        content_byte = response.raw.read(1024)
        
        # WAV文件传输结束
        if len(content_byte) == 0:
            break
            
        audio_out.write(content_byte)
        
    except Exception as ret:
        print("产生异常...", ret)
        audio_out.deinit()
        break
        
audio_out.deinit()

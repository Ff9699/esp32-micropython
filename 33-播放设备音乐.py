'''
i2s只能播放未压缩的音频（如wav格式），不能播放压缩过的音频（如mp3）。使用aconvert.com/cn/audio/网站转码。
'''
from machine import I2S
from machine import Pin

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
    rate=44100,         #设置为音频采样率
    ibuf=20000)

#建议使用
def play_music(wavtempfile):
    samples = bytearray(2048)
    with open(wavtempfile, "rb") as file:
        samples_read = file.readinto(samples)
        while samples_read > 0:
            audio_out.write(samples[:samples_read])
            samples_read = file.readinto(samples)


def play_music2(wavtempfile):
    #wavtempfile = "2.mp3"
    with open(wavtempfile, 'rb') as f:
        # 跳过文件的前44个字节
        pos = f.seek(44)
        
        # 用于存储音频数据的缓冲区
        wav_samples = bytearray(1024)
        wav_samples_mv = memoryview(wav_samples)
        
        print("开始播放音频...")
        
        # 播放音乐到I2S DAC
        while True:
            try:
                num_read = f.readinto(wav_samples_mv)
                
                if num_read == 0:
                    break
                
                # 输出解码后的WAV音频数据到I2S总线上
                num_written = 0
                while num_written < num_read:
                    num_written += audio_out.write(wav_samples_mv[num_written:num_read])
                    
            except Exception as ret:
                print("发生异常: ", ret)
                break

#play_music("test.wav")
#play_music("2.mp3")
play_music("Ding-dong-2s.wav")
#play_music("DingDong.wav")
from machine import Pin
import time

# 使用echo和trig引脚与HC-SR04超声波测距模块通信，echo是trig的输出，echo输出1的时间即为MCU的输入时间
# 超声波速度为340m/s，所以测量距离L = t * 340 / 2, t为MCU接收到回声的时间

def measure():
    # 测量开始前，先让trig输出低电平
    trig.value(1)
    time.sleep_us(10)
    trig.value(0)

    # 等待回声端口从低变高，开始记时
    while echo.value() == 0:
        t1 = time.ticks_us()
    
    print("-----------------")
    
    # 等待回声端口从高变低，结束记时
    while echo.value() == 1:
        t2 = time.ticks_us()
    
    print(t2)

    # 计算飞行时间t = ticks_ms(), ticks_us(), ticks_cpu()之间的差值, 得到t=ticks_us()
    # 超声波速度v=340m/s, 所以测量距离L=t*340/2/10000, 单位是米
    # 所以t2-t1=12848即得出L=12848 / 1000000 * 340 / 2 = 2.18米, 此处假设温度为30摄氏度所得出飞行速度v.
    # 计算时间差
    # t1 = time.ticks_ms(), t2 = time.ticks_us() / 1000, t3 = time.ticks_cpu()之间的时间差。这里用ticks_us()
    # 因为t1=t2=1时，ticks_ms()和ticks_us()都是返回340毫秒，但是需要除以1000000。此时的单位是秒，所以要乘以340计算出毫秒数来。
    # 或者t1=t2=12848时，ticks_ms()返回12848/1000毫秒，而ticks_us()/1000000返回12848/1000000秒

    # 计算距离 = (结束时间戳 - 开始时间戳) * 声速 / 2(来回)
    # t3 = time.ticks_diff(t2, t1) / 10000 # ticks_cpu()之间的差值, 转化为ticks_us()
    # t2-t1=12848是ms。0.000001s。声速340m/s，所以是声音走了12848 / 1000000 * 340的路程。但由于是从发射到接收，所以要除以2
    t3 = time.ticks_diff(t2, t1) / 10000
    print(t3, t2-t1)

    # 计算距离: 距离 = 时间*声音的传播速度/2（来回）
    return t3 * 340 / 2 * 10

# 引脚设置
trig = Pin(15, Pin.OUT)
echo = Pin(2, Pin.IN)
trig.value(0)
echo.value(0)

# try-except处理异常情况，避免except语句出错退出程序
try:
    while True:
        print("当前测量距离为:%.2f mm" % measure())
        time.sleep(1)

except KeyboardInterrupt:
    pass


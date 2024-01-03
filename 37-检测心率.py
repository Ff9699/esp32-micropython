from machine import sleep, SoftI2C, Pin, Timer                      # 导入所需的库
from utime import ticks_diff, ticks_us                             # 导入时间相关函数
from max30102 import MAX30102, MAX30105_PULSE_AMP_MEDIUM           # 导入MAX30102库

BEATS = 0  # 存储心率                                             # 初始化心率变量
FINGER_FLAG = False  # 默认表示未检测到手指                        # 初始化手指检测标志

def display_info(t):                                               # 显示数据的回调函数
    # 如果没有检测到手指，那么就不显示
    if FINGER_FLAG is False:
        return

    print('心率: ', BEATS)                                          # 显示心率

def main():                                                        # 主程序函数
    global BEATS, FINGER_FLAG  # 如果需要对全局变量修改，则需要global声明
    
    i2c = SoftI2C(sda=Pin(15), scl=Pin(2), freq=400000)              # 创建I2C对象(检测MAX30102)

    sensor = MAX30102(i2c=i2c)                                      # 创建传感器对象

    if sensor.i2c_address not in i2c.scan():                         # 检测是否有传感器
        print("没有找到传感器")
        return
    elif not (sensor.check_part_id()):                              # 检查传感器是否兼容
        print("检测到的I2C设备不是MAX30102或者MAX30105")
        return
    else:
        print("传感器已识别到")

    print("使用默认配置设置传感器")
    sensor.setup_sensor()                                           # 使用默认配置设置传感器

    sensor.set_sample_rate(400)                                     # 设置采样率
    sensor.set_fifo_average(8)                                      # 设置FIFO平均值
    sensor.set_active_leds_amplitude(MAX30105_PULSE_AMP_MEDIUM)      # 设置LED振幅

    t_start = ticks_us()                                            # 记录开始时间

    MAX_HISTORY = 32                                                # 历史数据列表长度
    history = []                                                    # 历史数据列表
    beats_history = []                                              # 心率历史数据列表
    beat = False                                                    # 心跳标志

    while True:
        sensor.check()                                              # 检测传感器状态
        if sensor.available():                                      # 如果传感器有数据可用
            red_reading = sensor.pop_red_from_storage()             # 从FIFO队列中获取红光数据
            ir_reading = sensor.pop_ir_from_storage()               # 从FIFO队列中获取红外数据
            
            if red_reading < 1000:                                  # 如果红光数据小于1000
                print('No finger')                                  # 打印没有检测到手指
                FINGER_FLAG = False                                 # 将手指检测标志置为False
                continue
            else:
                FINGER_FLAG = True                                  # 将手指检测标志置为True

            history.append(red_reading)                             # 将红光数据加入历史数据列表
            
            history = history[-MAX_HISTORY:]                        # 保留历史数据列表的后32个元素，防止内存溢出
            
            minima, maxima = min(history), max(history)             # 获取历史数据列表中的最小值和最大值
            threshold_on = (minima + maxima * 3) // 4               # 计算阈值（3/4）
            threshold_off = (minima + maxima) // 2                  # 计算阈值（1/2）
            
            if not beat and red_reading > threshold_on:             # 如果当前没有心跳且红光数据大于阈值（3/4）
                beat = True                                         # 将心跳标志置为True
                t_us = ticks_diff(ticks_us(), t_start)              # 计算时间差
                t_s = t_us/1000000                                  # 将微秒转换为秒
                f = 1/t_s                                           # 计算频率
                bpm = f * 60                                        # 计算心率
                if bpm < 500:                                       # 如果心率小于500
                    t_start = ticks_us()                            # 更新开始时间
                    beats_history.append(bpm)                       # 将心率加入心率历史数据列表
                    beats_history = beats_history[-MAX_HISTORY:]    # 保留心率历史数据列表的最后30个元素
                    BEATS = round(sum(beats_history)/len(beats_history), 2)  # 计算平均心率并四舍五入
            if beat and red_reading < threshold_off:                 # 如果当前有心跳且红光数据小于阈值（1/2）
                beat = False                                        # 将心跳标志置为False

if __name__ == '__main__':
    timer = Timer(1)                                               # 创建定时器
    timer.init(period=1000, mode=Timer.PERIODIC, callback=display_info)  # 设置定时器的回调函数，每1秒钟调用1次display_info函数（用来显示数据）
    main()                                                         # 调用主程序，用来检测数据

import machine  # 导入machine模块
import utime  # 导入utime模块
from machine import Pin  # 从machine模块导入Pin类


class IR(object):  # 定义IR类

    CODE = {  # 定义CODE字典
        162: "ch-", 98: "ch", 226: "ch+",
        34: "prev", 2: "next", 194: "play/stop",
        152: "0", 104: "*", 176: "#",
        224: "-", 168: "+", 144: "EQ",
        104: "0", 152: "100+", 176: "200+",
        48: "1", 24: "2", 122: "3",
        16: "4", 56: "5", 90: "6",
        66: "7", 74: "8", 82: "9"
    }

    def __init__(self, gpioNum):  # 定义初始化函数
        self.irRecv = machine.Pin(gpioNum, machine.Pin.IN, machine.Pin.PULL_UP)  # 定义irRecv为输入引脚，用于接收红外信号
        #Pin.IRQ_FALLING在下降沿中断。Pin.IRQ_RISING上升沿中断。Pin.IRQ_LOW_LEVEL低电平中断。Pin.IRQ_HIGH_LEVEL在高电平中断。
        # 配置中断信息，当红外信号的电平发生变化时，调用中断处理函数
        self.irRecv.irq(trigger=machine.Pin.IRQ_RISING | machine.Pin.IRQ_FALLING, handler=self.__handler)  
        self.ir_step = 0  # 用于记录红外信号解码的步骤
        self.ir_count = 0  # 用于记录红外信号解码的进度
        self.buf64 = [0 for i in range(64)]  # 初始化buf64为64个0的列表，用于存储接收到的红外信号数据
        self.recived_ok = False  # 表示是否成功接收到完整的红外信号
        self.cmd = None  # 用于存储解码后的红外信号命令
        self.cmd_last = None  # 用于存储上一次解码的红外信号命令
        self.repeat = 0  # 用于记录连续接收到相同红外信号的次数
        self.repeat_last = None  # 用于记录上一次连续接收到相同红外信号的次数
        self.t_ok = None  # 用于记录最后一次成功接收到红外信号的时间
        self.t_ok_last = None  # 用于记录上一次成功接收到红外信号的时间
        self.start = 0  # 用于记录红外信号接收的开始时间
        self.start_last = 0  # 用于记录上一次红外信号接收的开始时间
        self.changed = False  # 用于表示是否有新的红外信号接收

    def __handler(self, source):  # 定义中断回调函数
        """
        中断回调函数
        __handler函数是在IR类的__init__方法中通过self.irRecv.irq进行配置的，
        这样当红外信号的电平发生变化时，就会调用__handler函数。
        """
        thisComeInTime = utime.ticks_us()  # 获取当前时间

        # 更新时间
        curtime = utime.ticks_diff(thisComeInTime, self.start)  # 计算时间差
        print(curtime)
        self.start = thisComeInTime  # 更新start为当前时间
        
        
        if curtime >= 8500 and curtime <= 9500:  # 如果时间差在8500到9500之间,接受到前导码
            self.ir_step = 1  # 表示接收到了前导码。
            #print("收到前导码")
            print(f"收到前导码，数据间隔为{curtime}。")
            return  # 返回

        if self.ir_step == 1:  # 表示接收到了前导码。
            if curtime >= 4000 and curtime <= 5000:  # 正在接收红外信号
                self.ir_step = 2
                self.recived_ok = False
                self.ir_count = 0
                self.repeat = 0
                #print(f"步骤为{self.ir_step}，数据间隔为{curtime}。")
            elif curtime >= 2000 and curtime <= 3000:  # 连续接收到的相同红外信号。
                print(f"收到重复数据，重复{self.repeat}次，数据间隔为{curtime}。")
                self.ir_step = 3  
                self.repeat += 1
                

        elif self.ir_step == 2:  
            self.buf64[self.ir_count] = curtime  # 将当前时间差存入buf64
            self.ir_count += 1  
            if self.ir_count >= 64:  #成功接收到所有红外数据
                self.recived_ok = True  
                self.t_ok = self.start #记录最后ok的时间
                #print(f"步骤为{self.ir_step}，数据间隔为{curtime}。")
                #print(f"接收完成，数据：{self.buf64}")
                self.ir_step = 0  # 初始化步骤

        elif self.ir_step == 3:  # 连续接收到的相同红外信号。
            if curtime >= 500 and curtime <= 650:  # 如果时间差在500到650之间
                self.repeat += 1  # repeat加1
                print(f"步骤为{self.ir_step}，重复{self.repeat}次，数据间隔为{curtime}。")
        #print(f"第{self.ir_count}次，数据间隔为{curtime}。")
        #print(self.buf64)
    '''
    self.buf64为一个64个数据的列表，其中存储着脉冲时间，相邻两个脉冲时间组成一个二进制数据。
    如560+560为“0”，560+560*3为“1”。最终转换成32位二进制。
    '''
    def __check_cmd(self):  # 定义检查命令函数
        print("-----开始解码-----")
        print(f"待处理{len(self.buf64)}数据：{self.buf64}")
        byte4 = 0  #32位二进制整数，前补0
        for i in range(32):  
            x = i * 2  
            t = self.buf64[x] + self.buf64[x+1]  # t为buf64[x]和buf64[x+1]的和
            byte4 <<= 1  # byte4左移一位
            if t >= 1800 and t <= 2800:  # 如果t在1800到2800之间
                byte4 += 1  # byte4加1
        user_code_hi = (byte4 & 0xff000000) >> 24  # byte4的高8位，记录用户码高8位
        user_code_lo = (byte4 & 0x00ff0000) >> 16  # byte4的次高8位，记录用户码次高8位
        user_code = (user_code_hi << 8) | user_code_lo #高16位，记录用户码
        data_code = (byte4 & 0x0000ff00) >> 8      # byte4的次低8位，记录数据码
        data_code_r = byte4 & 0x000000ff           # byte4的低8位，记录数据反码
        self.cmd = data_code  
        print(f"处理后数据：{byte4} | {byte4:0>32b}")
        print(f"用户码：{user_code} | {user_code:0>16b}")
        print(f"数据码：{data_code} | {data_code:0>8b}")
        print(f"校验码：{data_code_r} | {data_code_r:0>8b}")


    def scan(self):  # 定义扫描函数
        # 接收到数据
        if self.recived_ok:  
            self.__check_cmd()  # 调用检查命令函数
            self.recived_ok = False  
            
        # 数据有变化
        if self.cmd != self.cmd_last or self.repeat != self.repeat_last or self.t_ok != self.t_ok_last:  # 如果cmd、repeat或t_ok有变化
            self.changed = True  # 设置changed为True
        else:  # 否则
            self.changed = False  # 设置changed为False

        # 更新
        self.cmd_last = self.cmd  
        self.repeat_last = self.repeat  
        self.t_ok_last = self.t_ok  
        # 对应按钮字符
        print(self.cmd)  # 打印cmd
        s = self.CODE.get(self.cmd)  # s为CODE字典中cmd对应的值
        return self.changed, s, self.repeat, self.t_ok  # 返回changed, s, repeat, t_ok



if __name__ == "__main__":  # 如果当前模块是主模块
    t = IR(15)  # 创建IR对象t
    
    while(True):  # 无限循环
        changed, s, repeat, t_ok = t.scan()  # 调用t的scan方法，获取返回值
        print(changed, s, repeat, t_ok)     #打印按键是否按下，按的是哪个键，重复了几次，
        utime.sleep(0.2)  # 暂停0.2秒
    


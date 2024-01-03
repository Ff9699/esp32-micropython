# 整体流程
# 1. 链接wifi
# 2. 启动网络功能（UDP）
# 3. 接收网络数据
# 4. 处理接收的数据


import socket
import time
import network
import machine


def do_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect('wifi帐号', 'wifi密码')
        i = 1
        while not wlan.isconnected():
            print("正在连接...等待{}s".format(i))
            i += 1
            time.sleep(1)
    print('network config:', wlan.ifconfig())


def start_udp():
    # 2. 启动网络功能（UDP）

    # 2.1. 创建udp套接字
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # 2.2. 绑定本地信息
    udp_socket.bind(("0.0.0.0", 7788))

    return udp_socket


def main():
    # 1. 链接wifi
    do_connect()
    # 2. 创建UDP
    udp_socket = start_udp()
    # 3. 创建灯对象
    led = machine.Pin(2, machine.Pin.OUT)
    # 4. 接收网络数据
    while True:
        #print(udp_socket.recvfrom(1024)) #(b'hello', ('192.168.5.226', 8080))
        recv_data, sender_info = udp_socket.recvfrom(1024)#拆分元组
        print("{}发送了消息：{}".format(sender_info, recv_data))#打印消息
        
        try:
            recv_data_str = recv_data.decode("utf-8")
            print("解码后的数据为：{}".format(recv_data_str))
        except Exception as ret:
            print("error:", ret)
            #recv_data_str = recv_data.decode("gbk")

        # 5. 处理接收的数据
        if recv_data_str == "light on":
            print("这里是要灯亮的代码...")
            led.value(1)
        elif recv_data_str == "light off":
            print("这里是要灯灭的代码...")
            led.value(0)


if __name__ == "__main__":
    main()

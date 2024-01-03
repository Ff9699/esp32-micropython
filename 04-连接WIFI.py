import network

#客户端模式
wlan = network.WLAN(network.STA_IF) # 创建站点接口
#wlan.active(False)
wlan.active(True)       # 激活接口
#wlan.scan()             # 扫描接入点
wlan.isconnected()      # 检查站点是否已连接到接入点
wlan.connect('wifi帐号', 'wifi密码') # 连接到接入点

wlan.config('mac')      # 获取接口的MAC地址
wlan.ifconfig()         # 获取接口的IP/子网掩码/网关/DNS地址
'''
wlan.disconnect()   #断开WiFi

#热点模式
ap = network.WLAN(network.AP_IF) # 创建接入点接口
ap.config(ssid='ESP-AP') # 设置接入点的SSID
ap.config(max_clients=10) # 设置可以连接到网络AA的客户端数量
ap.active(True)         # 激活接口

from socket import *
# 1. 创建udp套接字
udp_socket = socket(AF_INET, SOCK_DGRAM)
# 2. 准备接收方的地址
dest_addr = ('192.168.137.1', 8080)
# 3. 从键盘获取数据
send_data = "hello world"
# 4. 发送数据到指定的电脑上
udp_socket.sendto(send_data.encode('utf-8'), dest_addr)
# 5. 等待接受数据
recv_data = udp_socket.recvfrom(1024) # 1024表示本次接收的最大字节数
# 6. 显示对方发送的数据
# 接收到的数据recv_data是一个元组
# 第1个元素是对方发送的数据
# 第2个元素是对方的ip和端口
print(recv_data[0].decode('gbk'))
print(recv_data[1])
# 7. 关闭套接字
udp_socket.close()
'''
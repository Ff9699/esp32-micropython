from machine import Pin
import onewire, ds18x20
import time


ds_pin = Pin(13)
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))


def read_ds_sensor():
    roms = ds_sensor.scan()
    print('发现设备: ', roms)
    ds_sensor.convert_temp()
    for rom in roms:
        temp = ds_sensor.read_temp(rom)
        if isinstance(temp, float):
            temp = round(temp, 2)
            return temp
    # return 0  # 这里删除，那么默认此函数在没有获取到温度的时候返回为默认值None，调用处判断即可


while True:
    print(read_ds_sensor())
    time.sleep(1)

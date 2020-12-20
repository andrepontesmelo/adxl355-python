from lib.adxl355 import ADXL355

import time
import sys

device = ADXL355(1, 2)

while True:
    # x = device.get_acc_x()
    # y = device.get_acc_y()
    # z = device.get_acc_z()
    # temp = device.get_temp()

    # print(f'X: {x} \t Y: {y} \t Z:{z} \t TEMP: \t {temp}')

#    print("ID: {:X}".format(device.get_devid()))
    #print(f'TEMP: \t {device.get_temp()}')
    print(f'ACC X: \t {device.get_acc_x()}')

    time.sleep(3)

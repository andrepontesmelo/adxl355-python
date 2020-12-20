from lib.adxl355 import ADXL355

import time
import sys

device = ADXL355(0, 0)

while True:
    x = device.get_acc_x()
    y = device.get_acc_y()
    z = device.get_acc_z()
    temp = device.get_temp()

    print(f'X: {x} \t Y: {y} \t Z:{z} \t TEMP: \t {temp}')

    time.sleep(0.1)

from lib.adxl355 import ADXL355

import time
import sys

device = ADXL355(1, 2)

# first_x = device.get_acc_x()
# first_y = device.get_acc_y()
# first_z = device.get_acc_z()

first_x = 3.66521484375
first_y = 4.089890625
first_z = 3.15569921875

while True:
    print("ID: {:X}".format(device.get_devid()))
    print(f'TEMP: \t {device.get_temp()}')
    
    x = device.get_acc_x() 
    y = device.get_acc_y() 
    z = device.get_acc_z() 
    
    print(f'X: {round(abs(x - first_x), 2)}')
    print(f'Y: {round(abs(y - first_y), 2)}')
    print(f'Z: {round(abs(z - first_z), 2)}')

    print()

    time.sleep(.2)

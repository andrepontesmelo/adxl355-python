import spidev


class ADXL355:
    # Metainfo
    DEVID = 0x00

    # SPI config
    SPI_MAX_CLOCK_HZ = 10000000
    SPI_MODE = 0b00

    # Addresses
    XDATA3 = 0x08
    XDATA2 = 0x09
    XDATA1 = 0x0A
    YDATA3 = 0x0B
    YDATA2 = 0x0C
    YDATA1 = 0x0D
    ZDATA3 = 0x0E
    ZDATA2 = 0x0F
    ZDATA1 = 0x10
    TEMP2 = 0x06
    TEMP1 = 0x07
    RANGE = 0x2C
    POWER_CTL = 0x2D
    SELF_TEST = 0x2E
    FIFO_ENTRIES = 0x05
    FIFO_DATA = 0x11

    # Data Range
    RANGE_2G = 0x01
    RANGE_4G = 0x02
    RANGE_8G = 0x03

    # Values
    READ_BIT = 0x01
    WRITE_BIT = 0x00
    DUMMY_BYTE = 0xAA
    MEASURE_MODE = 0x06  # Only accelerometer

    # Settings:
    SELF_TEST_X_MIN = -0.2
    SELF_TEST_X_MAX = 0

    SELF_TEST_Y_MIN = 0
    SELF_TEST_Y_MAX = 0.6

    SELF_TEST_Z_MIN = -1.1
    SELF_TEST_Z_MAX = 1.3

    def __init__(self, bus, device, measure_range=RANGE_2G):
        # SPI init
        self.spi = spidev.SpiDev()
        self.spi.open(bus, device)
        self.spi.max_speed_hz = ADXL355.SPI_MAX_CLOCK_HZ
        self.spi.mode = ADXL355.SPI_MODE

        # Device init
        self._set_measure_range(measure_range)
        self._enable_measure_mode()

        self.range = measure_range

        ok = self.self_test()
        
        if not ok:
            print(f'Accelerometer: Self test not ok. Will not initialize.')
            self.spi = None

    def self_test(self):
        self.write_data(ADXL355.SELF_TEST, 0b11)
        x = self.get_acc_x()
        y = self.get_acc_y()
        z = self.get_acc_z()

        print(f'Accelerometer: SELF TEST X: {x}')
        print(f'Accelerometer: SELF TEST Y: {y}')
        print(f'Accelerometer: SELF TEST Z: {z}')

        ok = True
        if not (ADXL355.SELF_TEST_X_MIN <= x <= ADXL355.SELF_TEST_X_MAX):
            print(f'Accelerometer: Error - X out of test range: {ADXL355.SELF_TEST_X_MIN} <= {x} <= {ADXL355.SELF_TEST_X_MAX}')
            ok = False

        if not (ADXL355.SELF_TEST_Y_MIN <= y <= ADXL355.SELF_TEST_Y_MAX):
            print(f'Accelerometer: Error - Y out of test range: {ADXL355.SELF_TEST_Y_MIN} <= {y} <= {ADXL355.SELF_TEST_Y_MAX}')
            ok = False

        if not (ADXL355.SELF_TEST_Z_MIN <= z <= ADXL355.SELF_TEST_Z_MAX):
            print(f'Accelerometer: Error - Z out of test range: {ADXL355.SELF_TEST_Z_MIN} <= {z} <= {ADXL355.SELF_TEST_Z_MAX}')
            ok = False

        self.self_test_off()

        return ok

    def self_test_on(self):
        self.write_data(ADXL355.SELF_TEST, 0b11)

    def self_test_off(self):
        self.write_data(ADXL355.SELF_TEST, 0b00)

    def write_data(self, address, value):
        device_address = address << 1 | ADXL355.WRITE_BIT
        self.spi.xfer2([device_address, value])

    def read(self, register, length=1):
        address = (register << 1) | 0b1
        if length == 1:
            result = self.spi.xfer2([address, 0x00])
            return result[1]
        else:
            result = self.spi.xfer2([address] + [0x00] * (length))
            return result[1:]


    def _set_measure_range(self, measure_range):
        self.write_data(ADXL355.RANGE, measure_range)

    def _enable_measure_mode(self):
        self.write_data(ADXL355.POWER_CTL, ADXL355.MEASURE_MODE)

    def get_devid(self):
        return self.read(ADXL355.DEVID)

    def get_temp(self):
        high = self.read(ADXL355.TEMP2)
        low = self.read(ADXL355.TEMP1)
        #print(f'high = {bin(high)}')
        #print(f' low = {bin(low)}')

        high = (high & 0b00001111) << 8

        raw = high | low

        t = ((raw - 1852) / -9.05) + 25

        return t

    def get_acc_x(self):
        return self._get_axe(ADXL355.XDATA3)

    def get_acc_y(self):
        return self._get_axe(ADXL355.YDATA3)

    def get_acc_z(self):
        return self._get_axe(ADXL355.ZDATA3)

    def _two_comp(self, value):
        if (0x80000 & value):
            return - (0x0100000 - value)
        
        return value
         
    def print_bin(self, num):
        print(bin(num))

    def _get_axe(self, request):
        # Reading data
        raw = self.read(request, 3)

        return self._three_bytes_to_acc(raw, 0)

    def _three_bytes_to_acc(self, array, idx):
        print(f'will access idx: {idx}. Len = {len(array)}')
        high = array[idx] << 12
        
        mid = array[idx + 1] << 4

        low = array[idx + 2] >> 4

        result = high | mid | low

        result = self._two_comp(result)

        if self.range == ADXL355.RANGE_2G:
            result /= 256000
        elif self.range == ADXL355.RANGE_4G:
            result /= 128000
        elif self.range == ADXL355.RANGE_8G:
            result /= 64000
        else:
            raise Exception('Invalid Range')

        return result

    def get_fifo_valid_samples_count(self):
        count = self.read(ADXL355.FIFO_ENTRIES)
        return count

    def get_fifo(self):
        fifo = []
        count = self.read(ADXL355.FIFO_ENTRIES)

        array = self.read(ADXL355.FIFO_DATA, 3 * count)

        idx = 0

        for i in range(count // 3):
            print(f'i = {i}')
            x = self._three_bytes_to_acc(array, idx)
            idx += 3

            y = self._three_bytes_to_acc(array, idx)
            idx += 3
            
            z = self._three_bytes_to_acc(array, idx)
            idx += 3

            fifo.append([x,y,z])

        return fifo

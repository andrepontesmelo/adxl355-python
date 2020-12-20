import spidev


class ADXL355:
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

    # Data Range
    RANGE_2G = 0x01
    RANGE_4G = 0x02
    RANGE_8G = 0x03

    # Values
    READ_BIT = 0x01
    WRITE_BIT = 0x00
    DUMMY_BYTE = 0xAA
    MEASURE_MODE = 0x06  # Only accelerometer

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

        high = (high & 0b00001111) << 8

        raw = high + low

        t = ((raw - 1852) / -9.05) + 25

        return t

    def get_acc_x(self):
        return self._get_axe(ADXL355.XDATA3)

    def get_acc_y(self):
        return self._get_axe(ADXL355.YDATA3)

    def get_acc_z(self):
        return self._get_axe(ADXL355.ZDATA3)

    def _two_comp(self, val):
        if (0x80000 & val):
            val = val - (1 << 8)        # compute negative value

        return val    
    
    def _get_axe(self, request):
        # Reading data
        raw = self.read(request, 3)

        high = raw[0] << 12

        mid = raw[1] << 4

        low = raw[2] >> 4

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
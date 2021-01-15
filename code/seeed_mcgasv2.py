GM_RESOLUTION = 1023

GM_102B = 0x01
GM_302B = 0x03
GM_502B = 0x05
GM_702B = 0x07
CHANGE_I2C_ADDR = 0x55
WARMING_UP = 0xFE
WARMING_DOWN = 0xFF

class Gas(object):
    def __init__(self, i2c, address = 0x08):
        self.i2c = i2c
        self.address = address
        while not self.i2c.try_lock():
            pass
        self.i2c.writeto(self.address, bytes([WARMING_UP]))
        self.i2c.unlock()

    def measure_all(self):
        while not self.i2c.try_lock():
            pass

        self.i2c.writeto(self.address, bytes([GM_102B]))
        result = bytearray(4)
        self.i2c.readfrom_into(self.address, result)
        no2 = self.bytes_to_ppm(result)

        self.i2c.writeto(self.address, bytes([GM_302B]))
        result = bytearray(4)
        self.i2c.readfrom_into(self.address, result)
        c2h50h = self.bytes_to_ppm(result)

        self.i2c.writeto(self.address, bytes([GM_502B]))
        result = bytearray(4)
        self.i2c.readfrom_into(self.address, result)
        voc = self.bytes_to_ppm(result)

        self.i2c.writeto(self.address, bytes([GM_702B]))
        result = bytearray(4)
        self.i2c.readfrom_into(self.address, result)
        co = self.bytes_to_ppm(result)

        self.i2c.unlock()

        return [self.calcVol(no2), self.calcVol(c2h50h), self.calcVol(voc), self.calcVol(co)]

    def measure_NO2(self):
        while not self.i2c.try_lock():
            pass
        self.i2c.writeto(self.address, bytes([GM_102B]))
        result = bytearray(4)
        self.i2c.readfrom_into(self.address, result)
        self.i2c.unlock()
        return self.bytes_to_ppm(result)

    def measure_C2H50H(self):
        while not self.i2c.try_lock():
            pass
        self.i2c.writeto(self.address, bytes([GM_302B]), stop=False)
        result = bytearray(4)
        self.i2c.readfrom_into(self.address, result)
        self.i2c.unlock()
        return self.bytes_to_ppm(result)

    def measure_VOC(self):
        while not self.i2c.try_lock():
            pass
        self.i2c.writeto(self.address, bytes([GM_502B]), stop=False)
        result = bytearray(4)
        self.i2c.readfrom_into(self.address, result)
        self.i2c.unlock()
        return self.bytes_to_ppm(result)

    def measure_CO(self):
        while not self.i2c.try_lock():
            pass
        self.i2c.writeto(self.address, bytes([GM_702B]), stop=False)
        result = bytearray(4)
        self.i2c.readfrom_into(self.address, result)
        self.i2c.unlock()
        return self.bytes_to_ppm(result)

    def bytes_to_ppm(self, result):
        return result[0] + (result[1] << 8) + (result[2] << 16) + (result[3] << 24)

    def calcVol(self, adc):
        return (adc * 3.3) / GM_RESOLUTION

    def __del__(self):
        while not self.i2c.try_lock():
            pass
        self.i2c.writeto(self.address, bytes([WARMING_DOWN]), stop=True)
        self.i2c.unlock()

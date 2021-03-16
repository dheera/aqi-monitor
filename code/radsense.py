# Adapted from https://github.com/climateguard/RadSens

# Default radSens i2c device address
RS_DEFAULT_I2C_ADDRESS = 0x66  

#//Device id, default value: 0x7D
# //Size: 8 bit
RS_DEVICE_ID_RG = 0x00   

# Firmware version
# Size: 8 bit
RS_FIRMWARE_VER_RG = 0x01

# Radiation intensity (dynamic period T < 123 sec)
# Size: 24 bit
RS_RAD_INTENSY_DYNAMIC_RG = 0x03

# Radiation intensity (static period T = 500 sec)
# Size: 24 bit 
RS_RAD_INTENSY_STATIC_RG = 0x06

# Contains the accumulated number of pulses registered by the module
# since the last I2C data reading. The value is reset each
# time it is read. Allows you to process directly the pulses
# from the Geiger counter and implement other algorithms. The value is updated
# when each pulse is registered.
# Size: 16 bit
RS_PULSE_COUNTER_RG = 0x09

# This register is used to change the device address when multiple
# devices need to be connected to the same line at the same
# time. By default, it contains the value 0x66. At the end of recording, the new
# value is stored in the non-volatile memory of the microcontroller.
# Size: 8 bit 
# Access: R/W
RS_DEVICE_ADDRESS_RG = 0x10

# Control register for a high-voltage voltage Converter. By
# default, it is in the enabled state. To enable the HV generator,
# write 1 to the register, and 0 to disable it. If you try to write other
# values, the command is ignored.
# Size: 8 bit 
# Access: R/W
RS_HV_GENERATOR_RG = 0x11

# Contains the value coefficient used for calculating
# the radiation intensity. If necessary (for example, when installing a different
# type of counter), the necessary sensitivity value in
# imp/MKR is entered in the register. The default value is 105 imp/MKR. At the end of
# recording, the new value is stored in the non-volatile memory of the
# microcontroller.
# Size: 8 bit 
# Access: R/W
RS_SENSITIVITY_RG = 0x12

class Radsense_1_2(object):
    def __init__(self, i2c, address = RS_DEFAULT_I2C_ADDRESS):
        self.i2c = i2c
        self.address = address
        while not self.i2c.try_lock():
            pass
        self.i2c.writeto(self.address, bytes([0x0]))
        self.i2c.unlock()
        self._data = bytearray(19)

    def update_data(self):
        while not self.i2c.try_lock():
            pass
        self.i2c.readfrom_into(self.address, self._data)
        self.i2c.unlock()
        return self._data[0] == 0x7D # chip id

    def get_rad_intensity_dynamic(self):
        return ((self._data[3] << 16) | (self._data[4] << 8) | (self._data[5])) / 10.0

    def get_rad_intensity_static(self):
        return ((self._data[6] << 16) | (self._data[7] << 8) | (self._data[8])) / 10.0

    def get_pulse_count(self):
        return (self._data[9] << 8) | (self._data[10])

    def set_hv_generator_state(self, state):
        assert(type(state) is bool)
        while not self.i2c.try_lock():
            pass
        if state:
            self.i2c.writeto(self.address, bytes([RS_HV_GENERATOR_RG, 1]))
        else:
            self.i2c.writeto(self.address, bytes([RS_HV_GENERATOR_RG, 0]))
        self.i2c.unlock()

    def set_sensitivity(state, sensitivity):
        assert(type(sensitivity) is int)
        while not self.i2c.try_lock():
            pass
        self.i2c.writeto(self.address, [RS_HV_GENERATOR_RG, sensitivity])
        self.i2c.unlock()

    def __del__(self):
        pass

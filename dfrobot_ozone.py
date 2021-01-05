# -*- coding: utf-8 -*
""" 
  @file DFRobot_Ozone.py
  @note DFRobot_Ozone Class infrastructure, implementation of underlying methods
  @copyright   Copyright (c) 2010 DFRobot Co.Ltd (http://www.dfrobot.com)
  @licence     The MIT License (MIT)
  @author      [ZhixinLiu](zhixin.liu@dfrobot.com)
  version  V1.0
  date  2020-5-27
  @get from https://www.dfrobot.com
  @url https://github.com/DFRobot/DFRobot_Ozone
"""

ADDRESS_0                 = 0x70           # iic slave Address
ADDRESS_1                 = 0x71
ADDRESS_2                 = 0x72
ADDRESS_3                 = 0x73

MEASURE_MODE_AUTOMATIC    = 0x00           # active  mode
MEASURE_MODE_PASSIVE      = 0x01           # passive mode

AUTO_READ_DATA            = 0x00           # auto read ozone data
PASSIVE_READ_DATA         = 0x01           # passive read ozone data

MODE_REGISTER             = 0x03           # mode register
SET_PASSIVE_REGISTER      = 0x04           # read ozone data register

AUTO_DATA_HIGE_REGISTER   = 0x09           # auto data high eight bits
AUTO_DATA_LOW_REGISTER    = 0x0A           # auto data Low  eight bits

PASS_DATA_HIGE_REGISTER   = 0x07           # auto data high eight bits
PASS_DATA_LOW_REGISTER    = 0x08           # auto data Low  eight bits
  
class DFRobot_Ozone(object):
  __m_flag   = 0              # mode flag
  __count    = 0              # acquisition count    
  __txbuf      = [0]          # iic send buffer
  __ozonedata  = [0]*101      # ozone data
  def __init__(self, i2c, addr = ADDRESS_3):
    self.__addr = addr
    self.i2c = i2c

  ''' 
    @brief set the mode to read the data
    @param mode MEASURE_MODE_AUTOMATIC or MEASURE_MODE_PASSIVE
  '''
  def set_mode(self ,mode):
    if mode ==  MEASURE_MODE_AUTOMATIC:
      __m_flag = 0
      self.__txbuf[0] = MEASURE_MODE_AUTOMATIC 
      self.write_reg(MODE_REGISTER ,self.__txbuf)
    elif mode == MEASURE_MODE_PASSIVE:
      __m_flag = 1
      self.__txbuf[0] = MEASURE_MODE_PASSIVE
      self.write_reg(MODE_REGISTER ,self.__txbuf)
    else:
      __m_flag = 2
      return

  ''' 
    @brief get the ozone data ,units of PPB
    @param collectnum Collect the number
    @return  Ozone concentration, (units PPB)
  '''
  def get_ozone_data(self ,collectnum):
    if collectnum > 0:
      for num in range(collectnum ,1 ,-1):
        self.__ozonedata[num-1] = self.__ozonedata[num-2];
      if self.__m_flag == 0:
        self.__txbuf[0] = AUTO_READ_DATA
        self.write_reg(SET_PASSIVE_REGISTER ,self.__txbuf)
        self.__ozonedata[0] = self.get_ozone(AUTO_DATA_HIGE_REGISTER)
      elif self.__m_flag == 1:
        self.__txbuf[0] = PASSIVE_READ_DATA
        self.write_reg(SET_PASSIVE_REGISTER ,self.__txbuf)
        self.__ozonedata[0] = get_ozone(PASS_DATA_HIGE_REGISTER)
      if self.__count < collectnum:
        self.__count += 1
      return self.get_average_num(self.__ozonedata ,self.__count)
    elif (collectnum > 100) or (collectnum <= 0):
      return -1

  ''' 
    @brief get the average of the ozone data ,units of PPB
    @param barry ozone data group
    @param Len The number of data
    @return  Ozone concentration, (units PPB)
  '''
  def get_average_num(self ,barry ,Len):
    temp = 0
    for num in range (0 ,Len):
      temp += barry[num]
    return (temp / Len)

  ''' 
    @brief get the ozone data, units of PPB
    @param reg register address
    @return  Ozone concentration, (units PPB)
  '''
  def get_ozone(self,reg):
    rslt = self.read_reg(reg ,2)
    return ((rslt[0] << 8) + rslt[1])

  def write_reg(self, reg, data):
    while not self.i2c.try_lock():
        pass
    self.i2c.writeto(self.__addr, bytes([reg] + data))
    self.i2c.unlock()

  def read_reg(self, reg ,len):
    while not self.i2c.try_lock():
        pass
    self.i2c.writeto(self.__addr, bytes([reg]))
    result = bytearray(len)
    self.i2c.readfrom_into(self.__addr, result)
    self.i2c.unlock()
    return result

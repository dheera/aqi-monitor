print("Starting ...")

import time, gc, os
import board
import busio
import time
import freedomrobotics
#import adafruit_bno08x.i2ca

#from machine import I2C, Pin
print("import")
import adafruit_bme680
import adafruit_sgp30
import adafruit_tsl2591
import adafruit_scd30
import seeed_mcgasv2
import dfrobot_ozone
import adafruit_bno08x
from adafruit_bno08x.i2c import BNO08X_I2C
from adafruit_pm25.i2c import PM25_I2C

#i2c = busio.I2C(board.SCL, board.SDA, frequency=800000)
#bno = adafruit_bno08x.BNO08X(i2c)

print("init net")
from net import requests

print("init link")
link = freedomrobotics.NanoLink(requests = requests, auto_sync = False)

print("init i2c")
i2c = busio.I2C(board.SCL, board.SDA, frequency=800000)
link.log("info", "i2c initialized")
link.sync()

i2c1 = busio.I2C(board.IO17, board.IO18, frequency=100000)
link.log("info", "i2c1 initialized")
link.sync()

print("init bno08x")
bno = None
bno = BNO08X_I2C(i2c)

if bno is not None:
    bno.enable_feature(adafruit_bno08x.BNO_REPORT_ACCELEROMETER)
    bno.enable_feature(adafruit_bno08x.BNO_REPORT_GYROSCOPE)
    bno.enable_feature(adafruit_bno08x.BNO_REPORT_MAGNETOMETER)
    bno.enable_feature(adafruit_bno08x.BNO_REPORT_ROTATION_VECTOR)

link.log("info", "bno08x initialized")
link.sync()

print("init gas")
gas = None
gas = seeed_mcgasv2.Gas(i2c)

link.log("info", "mcgasv2 initialized")
link.sync()

print("init bme680")
bme680 = None
bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c)

link.log("info", "bme680 initialized")
link.sync()

print("init sgp30")
sgp30 = None
#sgp30 = adafruit_sgp30.Adafruit_SGP30(i2c)
if sgp30 is not None:
    print("SGP30 serial #", [hex(i) for i in sgp30.serial])
    sgp30.iaq_init()
    sgp30.set_iaq_baseline(0x8973, 0x8AAE)

link.log("info", "sgp30 initialized")
link.sync()

print("init scd30")
scd30 = None
scd30 = adafruit_scd30.SCD30(i2c)

link.log("info", "scd30 initialized")
link.sync()

print("init ozone")
ozone = None
ozone = dfrobot_ozone.DFRobot_Ozone(i2c)
if ozone is not None:
    ozone.set_mode(dfrobot_ozone.MEASURE_MODE_AUTOMATIC)

link.log("info", "ozone initialized")
link.sync()

print("init pm25")
pm25 = None
pm25 = PM25_I2C(i2c1, None)

link.log("info", "pm25 initialized")
link.sync()

while True:

    # print("\033[2J")
    # print("eCO2 = %d ppm TVOC = %d ppb" % (sgp30.eCO2, sgp30.TVOC))
    t = time.monotonic_ns()

    data = {}

    if pm25 is not None:
        try:
            aqdata = pm25.read()
            for key in aqdata:
               data["/pm25/" + key.replace(" ", "_")] = aqdata[key]
        except RuntimeError:
            print("Unable to read from sensor, retrying...")
            continue

    if scd30 is not None:
        try:
            if scd30.data_available:
                print("data available")
                #print("eCO2", scd30.eCO2, "ppm")
                #print("temp", scd30.temperature, "C")
                #print("hum", scd30.relative_humidity, "rH")
                data["/scd30/co2"] = scd30.eCO2
                data["/scd30/temp"] = scd30.temperature
                data["/scd30/hum"] = scd30.relative_humidity
                link.message("/scd30/co2", "std_msgs/Float32", {"data": scd30.eCO2})
                link.message("/scd30/humidity", "std_msgs/Float32", {"data": scd30.relative_humidity})
                link.message("/scd30/temp", "std_msgs/Float32", {"data": scd30.temperature})
        except:
            print("error reading scd30 data")

    if gas is not None:
        gas_data = gas.measure_all()
        data["/mcgasv2/raw"] = gas_data
        link.message("/mcgasv2/raw", "std_msgs/Float32", {"data": gas_data})

    if ozone is not None:
        ozone_ppb = ozone.get_ozone_data(10)
        data["/sen0321/ozone"] = ozone.get_ozone_data(10)
        link.message("/sen0321/ozone", "std_msgs/Float32", {"data": ozone_ppb})

    #print("eCO2 = %d ppm" % sgp30.eCO2)
    #print("TVOC = %d ppb" % sgp30.TVOC)
    #print('Light: {0}lux'.format(tsl2591.lux))
    #print('Visible: {0}'.format(tsl2591.visible))
    #print('Infrared: {0}'.format(tsl2591.infrared))

    if bme680 is not None:
        # print('pressure: {}hPa'.format(bme680.pressure))
        data["/bme680/pressure"] = bme680.pressure
        link.message("/bme680/pressure", "std_msgs/Float32", {"data": bme680.pressure})
    #print('Temperature: {} degrees C'.format(bme680.temperature))
    #print('Gas: {} ohms'.format(bme680.gas))
    #print('humidity: {}%'.format(bme680.humidity))
    # print('Light: {0}lux'.format(tsl2591.lux))
    # print('Visible: {0}'.format(tsl2591.visible))
    # print('Infrared: {0}'.format(tsl2591.infrared))

    if bno is not None:
        data["/bno085/acceleration"] = list(bno.acceleration)
        # print("acc", bno.acceleration)
        #print("gyr", bno.gyro)
        #print("mag", bno.magnetic)
        #print("quat", bno.quaternion)

    print(data)
    print("loop time", (time.monotonic_ns() - t)/1.0e6, "ms")

    link.sync()
    time.sleep(2)
    # requests.post("http://192.168.1.4:8888/devices/foo/data", headers = {"Content-Type": "application/json"}, json = data).content
    # requests.post("http://haystack.dheera.net/devices/aqm0/data", headers = {"Content-Type": "application/json", "Authorization": "Basic AXVubzpwQDU1dzByYM=="}, json = data).content


#while True:
#    quat = bno.rotation_vector
#    print("Rotation Vector Quaternion:")
#    print("I: %0.3f J: %0.3f K: %0.3f Accuracy: %0.3f"%(quat.i, quat.j, quat.k, quat.accuracy))


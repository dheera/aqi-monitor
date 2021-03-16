print("Starting ...")

import board
import busio
import display
import gc
import os
import sys
import time
import microcontroller
from config import *

time.sleep(5)

if LOAD_WATCHDOG:
    from watchdog import WatchDogMode
    w = microcontroller.watchdog
    w.timeout = 60.0
    w.mode = WatchDogMode.RESET
    w.feed()
    microcontroller.on_next_reset(microcontroller.RunMode.NORMAL)

print("import libraries")

if LOAD_FREEDOM:
    import freedomrobotics
if LOAD_BME680:
    import adafruit_bme680
if LOAD_SGP30:
    import adafruit_sgp30
if LOAD_SCD30:
    import adafruit_scd30
if LOAD_MCGASV2:
    import seeed_mcgasv2
if LOAD_SEN0321:
    import dfrobot_ozone
if LOAD_BNO08X:
    import adafruit_bno08x
    from adafruit_bno08x.i2c import BNO08X_I2C
if LOAD_PMSA003I:
    from adafruit_pm25.i2c import PM25_I2C
if LOAD_RADSENSE:
    import radsense
if LOAD_WATCHDOG:
    w.feed()

print("init i2c")
i2c = busio.I2C(board.SCL, board.SDA, frequency=800000)
if LOAD_PMSA003I:
    # PMSA003I needs its own i2c bus because it seems to mess with other i2c devices
    # it also needs a much lower i2c clock frequency per adafruit docs
    # fortunately the feathers2 has 2 i2c controllers and we can instantiate the 2nd one
    # on pins IO17 and IO18 which are very close to 3V and GND pins so
    # you can solder a JST-EH connector with 5 or more positions to [3V, 0, GND, 17, 18]
    # also, @unexpectedmaker warned on discord not to use IO0 for i2c
    i2c1 = busio.I2C(board.IO17, board.IO18, frequency=100000)

if LOAD_WATCHDOG:
    w.feed()

if LOAD_DISPLAY:
    print("init display")
    display.init(i2c)

    if LOAD_WATCHDOG:
        w.feed()

print("init net")
display.show(0, "init net")

from net import requests, geo

if LOAD_WATCHDOG:
    w.feed()

if LOAD_FREEDOM:
    print("init link")
    display.show(0, "init link")
    link = freedomrobotics.NanoLink(requests = requests, auto_sync = False)

    print("device:")
    print(link.device)

    if LOAD_WATCHDOG:
        w.feed()

def log(text):
    print(text)
    link.log("info", text)
    link.sync()


if LOAD_BNO08X:
    print("init bno08x")
    display.show(0, "init bno08x")
    link.log("info", "init bno08x")
    link.sync()

    bno = BNO08X_I2C(i2c)
    bno.enable_feature(adafruit_bno08x.BNO_REPORT_ACCELEROMETER)
    bno.enable_feature(adafruit_bno08x.BNO_REPORT_GYROSCOPE)
    bno.enable_feature(adafruit_bno08x.BNO_REPORT_MAGNETOMETER)
    bno.enable_feature(adafruit_bno08x.BNO_REPORT_ROTATION_VECTOR)

    if LOAD_WATCHDOG:
        w.feed()

if LOAD_MCGASV2:
    print("init mcgasv2")
    display.show(0, "init mcgasv2")
    link.log("info", "init mcgasv2")
    link.sync()

    gas = seeed_mcgasv2.Gas(i2c)

    if LOAD_WATCHDOG:
        w.feed()

if LOAD_BME680:
    print("init bme680")
    display.show(0, "init bme680")
    link.log("info", "init mcgasv2")
    link.sync()

    bme680 = None
    bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c)

    if LOAD_WATCHDOG:
        w.feed()

if LOAD_SGP30:
    print("init sgp30")
    display.show(0, "init sgp30")
    link.log("info", "init sgp30")
    link.sync()

    sgp30 = adafruit_sgp30.Adafruit_SGP30(i2c)
    print("SGP30 serial #", [hex(i) for i in sgp30.serial])
    sgp30.iaq_init()
    iaq_baseline = link.device.get("config.aqm.scd30", {}).get("iaq_baseline", [0x8973, 0x8AAE])
    if len(iaq_baseline) != 2 or type(iaq_baseline[0]) != int or type(iaq_baseline[1]) != int:
        iaq_baseline = [0x8973, 0x8AAE]
    sgp30.set_iaq_baseline(iaq_baseline[0], iaq_baseline[1])

    if LOAD_WATCHDOG:
        w.feed()

if LOAD_SCD30:
    print("init scd30")
    display.show(0, "init scd30")
    link.log("info", "init scd30")
    link.sync()

    scd30 = adafruit_scd30.SCD30(i2c)

    if LOAD_WATCHDOG:
        w.feed()

if LOAD_SEN0321:
    print("init sen0321")
    display.show(0, "init sen0321")
    link.log("info", "init sen0321")
    link.sync()

    ozone = dfrobot_ozone.DFRobot_Ozone(i2c)
    if ozone is not None:
        ozone.set_mode(dfrobot_ozone.MEASURE_MODE_AUTOMATIC)

    if LOAD_WATCHDOG:
        w.feed()

if LOAD_PMSA003I:
    print("init pm25")
    display.show(0, "init pm25")
    link.log("info", "init pm25")
    link.sync()

    pm25 = None
    pm25 = PM25_I2C(i2c1, None)

    if LOAD_WATCHDOG:
        w.feed()

if LOAD_RADSENSE:
    print("init radsense")
    display.show(0, "init radsense")
    link.log("info", "init radsense")
    link.sync()

    radsense = radsense.Radsense_1_2(i2c)

display_page = 0

seq = 0

while True:

    display_page = (display_page + 1) % 6

    t = time.monotonic_ns()

    data = []

    if LOAD_PMSA003I:
        try:
            aqdata_filtered = {}
            aqdata = pm25.read()
            for key in aqdata:
               aqdata_filtered[key.replace(" ", "_")] = aqdata[key]
            data.append(("/pmsa003i/raw", "pmsa003i_msgs/RawData", aqdata_filtered))
            data.append(("/pmsa003i/pm10_standard", "std_msgs/Float32", {"data": aqdata_filtered["pm10_standard"]}))
            data.append(("/pmsa003i/pm25_standard", "std_msgs/Float32", {"data": aqdata_filtered["pm25_standard"]}))
            data.append(("/pmsa003i/pm100_standard", "std_msgs/Float32", {"data": aqdata_filtered["pm100_standard"]}))
            if display_page == 0:
                display.show(0, "PM2.5:  %.1f" % aqdata_filtered["pm25_standard"])
                display.show(1, "PM10:   %.1f" % aqdata_filtered["pm10_standard"])
                display.show(2, "PM100:  %.1f" % aqdata_filtered["pm100_standard"])
        except RuntimeError:
            print("error reading pm25 data")

    if LOAD_SGP30:
        try:
            data.append(("/sgp30/tvoc", "std_msgs/Float32", {"data": sgp30.TVOC}))
            data.append(("/sgp30/eco2", "std_msgs/Float32", {"data": sgp30.eCO2}))
            data.append(("/sgp30/baseline_tvoc", "std_msgs/Float32", {"data": sgp30.baseline_TVOC}))
            data.append(("/sgp30/baseline_eco2", "std_msgs/Float32", {"data": sgp30.baseline_eCO2}))
            if display_page == 1:
                display.show(0, "eCO2:   %.2f ppm" % sgp30.eCO2)
                display.show(1, "TVOC:   %.2f ppb" % sgp30.TVOC)
                display.show(2, " ")
        except:
            print("error reading sgp30 data")

    if LOAD_SCD30:
        try:
            if scd30.data_available:
                co2 = scd30.eCO2
                humidity = scd30.relative_humidity
                temp = scd30.temperature
                if co2 > 0:
                    data.append(("/scd30/co2", "std_msgs/Float32", {"data": co2}))
                if humidity > 0:
                    data.append(("/scd30/humidity", "std_msgs/Float32", {"data": humidity}))
                if temp > 0:
                    data.append(("/scd30/temp", "std_msgs/Float32", {"data": temp}))
                if display_page == 2:
                    display.show(0, "CO2:   %.2f ppm" % co2)
                    display.show(1, "Hum:   %.2f pc" %humidity)
                    display.show(2, "Temp:  %.2f C" % temp)
        except:
            print("error reading scd30 data")

    if LOAD_MCGASV2:
        try:
            gas_data = gas.measure_all()
            data.append(("/mcgasv2/raw", "mcgasv2_msgs/RawData", {"gm102b": gas_data[0], "gm302b": gas_data[1], "gm502b": gas_data[2], "gm702b": gas_data[3]}))
            if display_page == 3:
                display.show(0, "102: %1.2f 302: %1.2f" % (gas_data[0], gas_data[1]))
                display.show(1, "502: %1.2f 702: %1.2f" % (gas_data[2], gas_data[3]))
                display.show(2, " ")
        except:
            print("error reading mcgasv2 data")

    if LOAD_SEN0321:
        try:
            ozone_ppb = ozone.get_ozone_data(10)
            data.append(("/sen0321/ozone", "std_msgs/Float32", {"data": ozone_ppb}))
            if display_page == 4:
                display.show(0, "O3: %.2f ppb" % ozone_ppb)
                display.show(1, " ")
                display.show(2, " ")
        except:
            print("error reading ozone data")

    if LOAD_BME680:
        try:
            data.append(("/bme680/pressure", "std_msgs/Float32", {"data": bme680.pressure}))
            if LOAD_SCD30:
                scd30.ambient_pressure = int(bme680.pressure)
            data.append(("/bme680/humidity", "std_msgs/Float32", {"data": bme680.relative_humidity}))
            data.append(("/bme680/temp", "std_msgs/Float32", {"data": bme680.temperature}))
            data.append(("/bme680/gas", "std_msgs/Float32", {"data": bme680.gas}))
            if display_page == 5:
                display.show(0, "Press: %.2f hPa" % bme680.pressure)
                display.show(1, "Temp:  %.2f C" % bme680.temperature)
                display.show(2, "Hum:   %.2f pc" % bme680.relative_humidity)
        except:
            print("error reading bme680 data")

    if LOAD_RADSENSE:
        try:
            radsense.update_data()
            data.append(("/radsense/pulse_count", "std_msgs/Int32", {"data": radsense.get_pulse_count()}))
            data.append(("/radsense/rad_intensity_dynamic", "std_msgs/Float32", {"data": radsense.get_rad_intensity_dynamic()}))
            data.append(("/radsense/rad_intensity_static", "std_msgs/Float32", {"data": radsense.get_rad_intensity_static()}))
        except Exception as e:
            print("error reading radsense data")
            sys.print_exception(e)

    if LOAD_BNO08X:
        pass
        # TODO: do something with IMU data (detect earthquakes?)
        # print("acc", bno.acceleration)
        # print("gyr", bno.gyro)
        # print("mag", bno.magnetic)
        # print("quat", bno.quaternion)

    if LOAD_FREEDOM:
        for topic, _type, msg in data:
            if "config.aqm.calibration" in link.device:
                if topic in link.device["config.aqm.calibration"]:
                    coeffs = link.device["config.aqm.calibration"][topic]
                    if "data" in msg:
                        in_value = msg["data"]
                        out_value = 0
                        for power, c in enumerate(coeffs):
                            out_value += c * in_value ** power
                        msg["data"] = out_value
        
            link.message(topic, _type, msg)

    if "location" in geo:
        link.message("/fix", "sensor_msgs/NavSatFix", {
            "header": {
                "seq": 0,
                "stamp": {
                    "secs": time.time(),
                    "nsecs": 0,
                },
                "frame_id": "base_link",
            },
            "latitude": geo["location"].get("lat", 0),
            "longitude": geo["location"].get("lng", 0),
            "position_covariance": [
                geo["location"].get("accuracy", 100),
                0,
                0,
                0,
                geo["location"].get("accuracy", 100),
                0,
                0,
                0,
                geo["location"].get("accuracy", 100)**2,
            ],
            "position_covariance_type": 1,
        })

    print("loop", (time.monotonic_ns() - t)/1.0e6, "ms")

    try:
        if LOAD_FREEDOM and link.sync():
            # sync to freedom was successful
            if LOAD_WATCHDOG:
                w.feed()
    except Exception as e:
        sys.print_exception(e)

    seq += 1

    time.sleep(2)

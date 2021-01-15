print("Starting ...")

import board
import busio
import gc
import os
import time
import microcontroller

LOAD_FREEDOM = True    # syncs data to device on freedomrobotics.ai; requires credentials.json with freedom device credentials
LOAD_WATCHDOG = True   # initiates a watchdog so the uc resets if any blocking call hangs for more than 30 seconds
LOAD_DISPLAY = True    # 128x32 OLED display: https://www.adafruit.com/product/4440
LOAD_BME680 = True     # pressure, humidity, temperature, voc: https://www.adafruit.com/product/3660
LOAD_SGP30 = True      # voc (better than bme680): https://www.adafruit.com/product/3709
LOAD_SCD30 = True      # co2, humidity, temp: https://www.seeedstudio.com/Grove-CO2-Temperature-Humidity-Sensor-SCD30-p-2911.html
LOAD_MCGASV2 = True    # multi-channel gas sensor: https://www.seeedstudio.com/Grove-Multichannel-Gas-Sensor-v2-p-4569.html
LOAD_SEN0321 = True    # ozone sensor: https://www.dfrobot.com/product-2005.html
LOAD_BNO08X = True     # imu: https://www.adafruit.com/product/4754
LOAD_PMSA003I = True   # air quality particulate matter sensor: https://www.adafruit.com/product/4632

if LOAD_WATCHDOG:
    from watchdog import WatchDogMode
    w = microcontroller.watchdog
    w.timeout = 30.0
    w.mode = WatchDogMode.RESET
    w.feed()
    microcontroller.on_next_reset(microcontroller.RunMode.NORMAL)

print("import libraries")

if LOAD_FREEDOM:
    import freedomrobotics
if LOAD_DISPLAY:
    import displayio
    import terminalio
    import adafruit_displayio_ssd1306
    from adafruit_display_text import label
    displayio.release_displays()
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
    from adafruit_pm25.i2c import PMSA003I_I2C
if LOAD_WATCHDOG:
    w.feed()

print("init i2c")
i2c = busio.I2C(board.SCL, board.SDA, frequency=800000)
i2c1 = busio.I2C(board.IO17, board.IO18, frequency=100000)

if LOAD_WATCHDOG:
    w.feed()

if LOAD_DISPLAY:
    print("init display")
    display_bus = displayio.I2CDisplay(i2c, device_address=0x3c)
    WIDTH = 128
    HEIGHT = 32
    display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=WIDTH, height=HEIGHT)
    splash = displayio.Group(max_size=10)
    display.show(splash)
    color_bitmap = displayio.Bitmap(WIDTH, HEIGHT, 1)
    color_palette = displayio.Palette(1)
    color_palette[0] = 0x000000 # White
    bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)

    splash.append(bg_sprite)
    text = " "
    text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=0, y=3)
    splash.append(text_area)
    text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=0, y=13)
    splash.append(text_area)
    text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=0, y=23)
    splash.append(text_area)

if LOAD_WATCHDOG:
    w.feed()

def display(line, text):
    if LOAD_DISPLAY:
        text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=0, y=3+10*line)
        splash[1+line] = text_area

display

print("init net")
display(0, "init net")
from net import requests

if LOAD_WATCHDOG:
    w.feed()

print("init link")
display(0, "init link")
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
    display(0, "init bno08x")
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
    display(0, "init mcgasv2")
    link.log("info", "init mcgasv2")
    link.sync()

    gas = seeed_mcgasv2.Gas(i2c)

    if LOAD_WATCHDOG:
        w.feed()

if LOAD_BME680:
    print("init bme680")
    display(0, "init bme680")
    link.log("info", "init mcgasv2")
    link.sync()

    bme680 = None
    bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c)

    if LOAD_WATCHDOG:
        w.feed()

if LOAD_SGP30:
    print("init sgp30")
    display(0, "init sgp30")
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
    display(0, "init scd30")
    link.log("info", "init scd30")
    link.sync()

    scd30 = adafruit_scd30.SCD30(i2c)

    if LOAD_WATCHDOG:
        w.feed()

if LOAD_SEN0321:
    print("init sen0321")
    display(0, "init sen0321")
    link.log("info", "init sen0321")
    link.sync()

    ozone = dfrobot_ozone.DFRobot_Ozone(i2c)
    if ozone is not None:
        ozone.set_mode(dfrobot_ozone.MEASURE_MODE_AUTOMATIC)

    if LOAD_WATCHDOG:
        w.feed()

if LOAD_PMSA003I:
    print("init pm25")
    display(0, "init pm25")
    link.log("info", "init pm25")
    link.sync()

    pm25 = None
    pm25 = PMSA003I_I2C(i2c1, None)

    if LOAD_WATCHDOG:
        w.feed()

display_page = 0

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
                display(0, "PM2.5:  %.1f" % aqdata_filtered["pm25_standard"])
                display(1, "PM10:   %.1f" % aqdata_filtered["pm10_standard"])
                display(2, "PM100:  %.1f" % aqdata_filtered["pm100_standard"])
        except RuntimeError:
            print("error reading pm25 data")

    if LOAD_SGP30:
        try:
            data.append(("/sgp30/tvoc", "std_msgs/Float32", {"data": sgp30.TVOC}))
            data.append(("/sgp30/eco2", "std_msgs/Float32", {"data": sgp30.eCO2}))
            data.append(("/sgp30/baseline_tvoc", "std_msgs/Float32", {"data": sgp30.baseline_TVOC}))
            data.append(("/sgp30/baseline_eco2", "std_msgs/Float32", {"data": sgp30.baseline_eCO2}))
            if display_page == 1:
                display(0, "eCO2:   %.2f ppm" % sgp30.eCO2)
                display(1, "TVOC:   %.2f ppb" % sgp30.TVOC)
                display(2, " ")
        except:
            print("error reading sgp30 data")

    if LOAD_SCD30:
        try:
            if scd30.data_available:
                data.append(("/scd30/co2", "std_msgs/Float32", {"data": scd30.eCO2}))
                data.append(("/scd30/humidity", "std_msgs/Float32", {"data": scd30.relative_humidity}))
                data.append(("/scd30/temp", "std_msgs/Float32", {"data": scd30.temperature}))
                if display_page == 2:
                    display(0, "CO2:   %.2f ppm" % scd30.eCO2)
                    display(1, "Hum:   %.2f pc" % scd30.relative_humidity)
                    display(2, "Temp:  %.2f C" % scd30.temperature)
        except:
            print("error reading scd30 data")

    if LOAD_MCGASV2:
        try:
            gas_data = gas.measure_all()
            data.append(("/mcgasv2/raw", "mcgasv2_msgs/RawData", {"gm102b": gas_data[0], "gm302b": gas_data[1], "gm502b": gas_data[2], "gm702b": gas_data[3]}))
            if display_page == 3:
                display(0, "102: %1.2f 302: %1.2f" % (gas_data[0], gas_data[1]))
                display(1, "502: %1.2f 702: %1.2f" % (gas_data[2], gas_data[3]))
                display(2, " ")
        except:
            print("error reading mcgasv2 data")

    if LOAD_SEN0321:
        try:
            ozone_ppb = ozone.get_ozone_data(10)
            data.append(("/sen0321/ozone", "std_msgs/Float32", {"data": ozone_ppb}))
            if display_page == 4:
                display(0, "O3: %.2f ppb" % ozone_ppb)
                display(1, " ")
                display(2, " ")
        except:
            print("error reading ozone data")

    if LOAD_BME680:
        try:
            data.append(("/bme680/pressure", "std_msgs/Float32", {"data": bme680.pressure}))
            if scd30 is not None:
                scd30.ambient_pressure = int(bme680.pressure)
            data.append(("/bme680/humidity", "std_msgs/Float32", {"data": bme680.relative_humidity}))
            data.append(("/bme680/temp", "std_msgs/Float32", {"data": bme680.temperature}))
            data.append(("/bme680/gas", "std_msgs/Float32", {"data": bme680.gas}))
            if display_page == 5:
                display(0, "Press: %.2f hPa" % bme680.pressure)
                display(1, "Temp:  %.2f C" % bme680.temperature)
                display(2, "Hum:   %.2f pc" % bme680.relative_humidity)
        except:
            print("error reading bme680 data")

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

    print("loop", (time.monotonic_ns() - t)/1.0e6, "ms")

    if LOAD_FREEDOM and link.sync():
        # sync to freedom was successful
        if LOAD_WATCHDOG:
            w.feed()

    time.sleep(2)



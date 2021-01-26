import adafruit_requests
import ipaddress
import json
import re
import rtc
import socketpool
import ssl
import time
import wifi
 
try:
    with open("wifi.json") as f:
        config_wifi = json.loads(f.read())
except ImportError:
    print("WiFi secrets are kept in wifi.json, please add them there!")
    raise
 
print("mac address:", [hex(i) for i in wifi.radio.mac_address])
 
print("available wifi networks:")
for network in wifi.radio.start_scanning_networks():
    print("\t%s\t\tRSSI: %d\tChannel: %d" % (str(network.ssid, "utf-8"),
            network.rssi, network.channel))
wifi.radio.stop_scanning_networks()
 
print("connecting to %s" % config_wifi["ssid"])
wifi.radio.connect(config_wifi["ssid"], config_wifi["password"])
print("connected to %s! " % config_wifi["ssid"])
print("ip address:", wifi.radio.ipv4_address)
 
pool = socketpool.SocketPool(wifi.radio)
requests = adafruit_requests.Session(pool, ssl.create_default_context())

print("setting system time")

def time_set(utc_time):
    r = rtc.RTC()
    r.datetime = utc_time
    print("setting system time to:", utc_time)

def time_sync():
    i = 0
    while True:
        print("trying api.freedomrobotics.ai ... (%d)" % i)
        response = requests.get("https://api.freedomrobotics.ai/utc_now", timeout = 10)
        if response.status_code == 200:
            # the following is a hack to convert freedom's time response to an integer
            # before JSON decoding it since circuitpython only has single-precision floats
            # which will mangle the time
            content = re.sub("\\.[0-9]+", "", response.content)
            utc_time = time.localtime(int(json.loads(content)["timestamp"]))
            print("setting time to", utc_time)
            time_set(utc_time)
            break

        print("trying worldtimeapi.org ... (%d)" % i)
        response = requests.get("http://worldtimeapi.org/api/timezone/Etc/UTC", timeout = 10)
        if response.status_code == 200:
            utc_time = time.localtime(int(json.loads(response.content)["unixtime"]))
            print("setting time to", utc_time)
            time_set(utc_time)
            break 

        i += 1

        if i >= 10:
            raise Exception("Time set failed")

        time.sleep(1.0)

print("time is", time.time())

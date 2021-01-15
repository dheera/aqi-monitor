import adafruit_requests
import ipaddress
import json
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

response = requests.get("http://worldtimeapi.org/api/timezone/Etc/UTC")
if response.status_code == 200:
    r = rtc.RTC()
    r.datetime = time.localtime(json.loads(response.content)["unixtime"])
    print(f"system Time: {r.datetime}")
else:
    print("setting time failed")


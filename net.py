import adafruit_requests
import ipaddress
import json
import rtc
import socketpool
import ssl
import time
import wifi

 
# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise
 
print("ESP32-S2 WebClient Test")
 
print("My MAC addr:", [hex(i) for i in wifi.radio.mac_address])
 
print("Available WiFi networks:")
for network in wifi.radio.start_scanning_networks():
    print("\t%s\t\tRSSI: %d\tChannel: %d" % (str(network.ssid, "utf-8"),
            network.rssi, network.channel))
wifi.radio.stop_scanning_networks()
 
print("Connecting to %s"%secrets["ssid"])
wifi.radio.connect(secrets["ssid"], secrets["password"])
print("Connected to %s!"%secrets["ssid"])
print("My IP address is", wifi.radio.ipv4_address)
 
#ipv4 = ipaddress.ip_address("8.8.4.4")
#print("Ping google.com: %f ms" % (wifi.radio.ping(ipv4)*1000))
 
pool = socketpool.SocketPool(wifi.radio)
requests = adafruit_requests.Session(pool, ssl.create_default_context())

print("Setting system time")

response = requests.get("http://worldtimeapi.org/api/timezone/Etc/UTC")
if response.status_code == 200:
    r = rtc.RTC()
    r.datetime = time.localtime(json.loads(response.content)["unixtime"])
    print(f"System Time: {r.datetime}")
else:
    print("Setting time failed")


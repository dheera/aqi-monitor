import adafruit_requests
import ipaddress
import json
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
 
print("mac address:", "%02x:%02x:%02x:%02x:%02x:%02x" % tuple(map(int, wifi.radio.mac_address)))

print("available wifi networks:")
accessPoints = []
for network in wifi.radio.start_scanning_networks():
    #print("\t%s\t\tRSSI: %d\tChannel: %d" % (str(network.ssid, "utf-8"),
    #        network.rssi, network.channel))
    accessPoints.append({
        "macAddress": "%02x:%02x:%02x:%02x:%02x:%02x" % tuple(network.bssid),
        "age": 0,
        "signalLevel": network.rssi,
        "channel": network.channel,
        "ssid": network.ssid,
    })
print(accessPoints)
wifi.radio.stop_scanning_networks()
 
print("connecting to %s" % config_wifi["ssid"])
wifi.radio.connect(config_wifi["ssid"], config_wifi["password"])
print("connected to %s! " % config_wifi["ssid"])
print("ip address:", wifi.radio.ipv4_address)
 
pool = socketpool.SocketPool(wifi.radio)
requests = adafruit_requests.Session(pool, ssl.create_default_context())

print("attempting to geolocate ...")
geo = {}
try:
    r = requests.post(
        "https://location.services.mozilla.com/v1/geolocate?key=test",
        json = {
            "radioType": "gsm",
            "considerIp": "true",
            "wifiAccessPoints": accessPoints,
        },
        timeout = 5
    )
    geo = json.loads(r.content)
    print(geo)
except:
    print("geolocation error")

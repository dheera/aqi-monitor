import sys
import time
import json

UPLOAD_QUEUE_MAX_SIZE = 127
LOG_LEVELS = {"debug": 1, "info": 2, "warn": 4, "warning": 4, "error": 8, "fatal": 16}
DEBUG = 1
INFO = 2
WARN = 4
ERROR = 8
FATAL = 16

def get_utc_now(requests):
    url = "https://api.freedomrobotics.ai/utc_now"
    response = requests.get(url)
    if response.status_code == 200:
        return time.localtime(json.loads(response.content)["timestamp"])
    return None

class NanoLink(object):
    def __init__(self, account = None, device = None, token = None, secret = None, auto_sync = True, requests = None, debug = False):
        self.debug = debug
        self.requests = requests
        if self.requests is None:
            import requests
            self.requests = requests

        if account is None or device is None or token is None or secret is None:
            with open("credentials.json") as f:
                credentials = json.loads(f.read())
            self.account = credentials["account"]
            self.device = credentials["device"]
            self.token = credentials["token"]
            self.secret = credentials["secret"]
        else:
            self.account = account
            self.device = device
            self.token = token
            self.secret = secret

        self._url = "https://api.freedomrobotics.ai/"
        self._device_url = "%s/accounts/%s/devices/%s" % (self._url.strip("/"), self.account, self.device)
        self._data_url = "%s/accounts/%s/devices/%s/data" % (self._url.strip("/"), self.account, self.device)
        self.auto_sync = auto_sync
        self._outgoing_message_queue = []
        self.device = {}
        self._update_device()

    def _update_device(self):
        headers = {
            "mc_token": self.token,
            "mc_secret": self.secret,
        }
        try:
            result = self.requests.get(
                self._device_url,
                headers = headers,
                timeout = 10,
            )
            if result.status_code != 200:
                print("[freedomrobotics] update device error: " + str(result.status_code) + ": " + result.content)
                return False
        except:
            print("[freedomrobotics] update device error")
            return False
        
        self.device = json.loads(result.content)
        self._last_update_device_time = time.monotonic_ns() / 1e9

        return True

    def sync(self):
        if time.monotonic_ns() / 1e9 - self._last_update_device_time > 1800:
            self._update_device()

        headers = {
            "mc_token": self.token,
            "mc_secret": self.secret,
        }
        if self.debug:
            print(self._data_url)
            print(headers)
            print(self._outgoing_message_queue)

        try:
            result = self.requests.put(
                self._data_url,
                headers = headers,
                json = self._outgoing_message_queue,
                timeout = 5,
            )
            if self.debug:
                print(result.status_code, result.content)

            if result.status_code != 200:
                print("[freedomrobotics] sync error: " + str(result.status_code) + ": " + result.content)
                return False
            else:
                self._outgoing_message_queue = []
        except Exception as e:
            sys.print_exception(e)
            raise Exception("[freedomrobotics] sync error")
            return False

        return True

    def log(self, level, msg, stack_trace=None):
        if type(level) is str:
            level_int = LOG_LEVELS[level]
        else:
            level_int = level

        self.message(
            "/logs",
            "freedom_msgs/Log",
            {
                "level": level_int,
                "name": "nanolink",
                "file": "nanolink",
                "function": "nanolink",
                "line": 0,
                "msg": msg,
            }
        )

    def message(self, topic, topic_type, msg):
        self._outgoing_message_queue.append({
              "platform": "ros",
              "utc_time": time.time(),
              "topic": topic,
              "type": topic_type,
              "data": msg,
        })

        while len(self._outgoing_message_queue) > UPLOAD_QUEUE_MAX_SIZE:
            del(self._outgoing_message_queue[0])

        if self.auto_sync:
            self.sync()

if __name__ == "__main__":
    print("Running test")

    import json
    import random
    import time

    link = NanoLink()

    while True:
        time.sleep(0.5)
        value = random.random()
        print("Sending " + str(value))
        link.message("/random", "std_msgs/Float32", {"data": value})


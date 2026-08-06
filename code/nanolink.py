import json
import rtc
import sys
import time

__version__ = "2.0.0"

LOG_LEVELS = {"debug": 1, "info": 2, "warn": 4, "warning": 4, "error": 8, "fatal": 16}
DEBUG = 1
INFO = 2
WARN = 4
ERROR = 8
FATAL = 16

class NanoLink(object):
    """Streams sensor data as JSON to a self-hosted ingestion server (see server/)."""

    def __init__(self, url = None, device_id = None, api_key = None, auto_sync = True, auto_time_sync = True, requests = None, debug = False, max_queue_size = 127):
        self.__version__ = __version__
        self.auto_sync = auto_sync
        self.debug = debug
        self.requests = requests
        self.max_queue_size = max_queue_size
        self.config = {}

        if self.requests is None:
            import requests
            self.requests = requests

        if url is None or device_id is None or api_key is None:
            with open("credentials.json") as f:
                credentials = json.loads(f.read())
            self.url = credentials["url"]
            self.device_id = credentials["device_id"]
            self.api_key = credentials["api_key"]
        else:
            self.url = url
            self.device_id = device_id
            self.api_key = api_key

        self._time_url = "%s/utc_now" % self.url.rstrip("/")
        self._data_url = "%s/devices/%s/data" % (self.url.rstrip("/"), self.device_id)
        self._config_url = "%s/devices/%s/config" % (self.url.rstrip("/"), self.device_id)
        self._outgoing_message_queue = []

        if auto_time_sync:
            self.sync_time()

        self.fetch_config()

    def sync_time(self):
        try:
            result = self.requests.get(self._time_url, timeout = 10)
            if result.status_code == 200:
                utc_time = time.localtime(int(json.loads(result.content)["timestamp"]))
                rtc.RTC().datetime = utc_time
                return True
            else:
                print("[nanolink] sync_time error: " + str(result.status_code))
        except Exception:
            print("[nanolink] sync_time error")

        return False

    def fetch_config(self):
        headers = {"x-api-key": self.api_key}
        try:
            result = self.requests.get(self._config_url, headers = headers, timeout = 10)
            if result.status_code == 200:
                self.config = json.loads(result.content)
            else:
                print("[nanolink] fetch_config error: " + str(result.status_code))
        except Exception:
            print("[nanolink] fetch_config error")

        return self.config

    def sync(self):
        if not self._outgoing_message_queue:
            return True

        headers = {
            "x-api-key": self.api_key,
            "content-type": "application/json",
        }

        if self.debug:
            print(self._data_url)
            print(self._outgoing_message_queue)

        try:
            result = self.requests.post(
                self._data_url,
                headers = headers,
                json = self._outgoing_message_queue,
                timeout = 5,
            )
            if result.status_code != 200:
                print("[nanolink] sync error: " + str(result.status_code) + ": " + result.content)
                return False
            else:
                self._outgoing_message_queue = []
        except Exception as e:
            sys.print_exception(e)
            return False

        return True

    def log(self, level, msg, stack_trace=None):
        if type(level) is str:
            level_int = LOG_LEVELS[level]
        else:
            level_int = level

        self.message(
            "/logs",
            "log_msgs/Log",
            {
                "level": level_int,
                "msg": msg,
            }
        )

    def message(self, topic, topic_type, msg):
        self._outgoing_message_queue.append({
            "utc_time": time.time(),
            "topic": topic,
            "type": topic_type,
            "data": msg,
        })

        while len(self._outgoing_message_queue) > self.max_queue_size:
            del(self._outgoing_message_queue[0])

        if self.auto_sync:
            self.sync()

if __name__ == "__main__":
    print("Running test")

    import random

    link = NanoLink()

    while True:
        time.sleep(0.5)
        value = random.random()
        print("Sending " + str(value))
        link.message("/random", "std_msgs/Float32", {"data": value})

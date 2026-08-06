import json
import os
import time
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException, Request
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

API_KEY = os.environ["API_KEY"]
INFLUXDB_URL = os.environ.get("INFLUXDB_URL", "http://influxdb:8086")
INFLUXDB_TOKEN = os.environ["INFLUXDB_TOKEN"]
INFLUXDB_ORG = os.environ["INFLUXDB_ORG"]
INFLUXDB_BUCKET = os.environ.get("INFLUXDB_BUCKET", "aqi")
DEVICES_DIR = Path(os.environ.get("DEVICES_DIR", "/devices"))

app = FastAPI()
client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)


def check_api_key(x_api_key):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="invalid api key")


def flatten(prefix, value, out):
    if isinstance(value, dict):
        for key, val in value.items():
            flatten("%s_%s" % (prefix, key) if prefix else key, val, out)
    elif isinstance(value, (list, tuple)):
        out[prefix] = json.dumps(value)
    else:
        out[prefix] = value


@app.get("/utc_now")
async def utc_now():
    return {"timestamp": int(time.time())}


@app.post("/devices/{device_id}/data")
async def post_data(device_id: str, request: Request, x_api_key: str = Header(None)):
    check_api_key(x_api_key)
    messages = await request.json()

    written = 0
    for msg in messages:
        topic = msg.get("topic", "unknown").strip("/").replace("/", "_") or "root"

        fields = {}
        flatten("", msg.get("data", {}), fields)
        fields = {k: v for k, v in fields.items() if isinstance(v, (int, float, str, bool))}
        if not fields:
            continue

        point = Point(topic).tag("device", device_id)
        for key, val in fields.items():
            point = point.field(key, val)
        point = point.time(int(msg.get("utc_time", time.time())), write_precision="s")

        write_api.write(bucket=INFLUXDB_BUCKET, record=point)
        written += 1

    return {"status": "ok", "written": written}


@app.get("/devices/{device_id}/config")
async def get_config(device_id: str, x_api_key: str = Header(None)):
    check_api_key(x_api_key)
    path = DEVICES_DIR / ("%s.json" % device_id)
    if not path.exists():
        return {}
    return json.loads(path.read_text())

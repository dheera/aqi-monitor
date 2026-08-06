# aqi-monitor server

Self-hosted replacement for the (now defunct) Freedom Robotics upload target. Runs three
containers on your LAN:

- **influxdb** — time-series database that stores the sensor readings
- **receiver** — small HTTP API the microcontroller posts JSON to; writes into InfluxDB
- **grafana** — dashboards and alerting on top of InfluxDB, pre-provisioned with a
  datasource and a starter dashboard (`grafana/provisioning/dashboards/aqi-monitor.json`)

## Setup

1. Copy the env template and fill in real secrets:

   ```
   cp .env.example .env
   ```

   Generate `INFLUXDB_TOKEN` and `API_KEY` as long random strings (e.g. `openssl rand -hex 32`).

2. Add a config file for each device under `devices/<device_id>.json` (an example is
   already there for `aqi-monitor-01`). This is where SGP30 IAQ baselines and any
   per-topic calibration coefficients live; the microcontroller fetches this at boot via
   `GET /devices/<device_id>/config`.

3. Start the stack:

   ```
   docker compose up -d --build
   ```

4. Grafana is at `http://<host>:3000` (login `admin` / `GRAFANA_PASSWORD` from `.env`).
   InfluxDB's own UI is at `http://<host>:8086` if you want to query data directly.

5. On the microcontroller, point `code/credentials.json` at this server:

   ```json
   {
     "url": "http://<host>:8080",
     "device_id": "aqi-monitor-01",
     "api_key": "<same value as API_KEY in .env>"
   }
   ```

## Data model

The receiver flattens each incoming message's nested `data` dict into InfluxDB fields
(e.g. `{"pm25_standard": 12}` under topic `pmsa003i/pm25_standard` becomes measurement
`pmsa003i_pm25_standard`, field `data`). Every point is tagged with `device=<device_id>`,
so a single stack can ingest multiple monitors.

## Long-term archival (optional)

InfluxDB retention can be capped and older data exported/archived to S3 on a schedule
(e.g. `influx backup` + a cron job pushing to a bucket) if you want cheap cold storage
beyond what you keep live in Grafana. This isn't set up by default.

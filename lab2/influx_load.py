import math
from datetime import datetime, timedelta, timezone
from influxdb_client import InfluxDBClient, Point, WriteOptions

URL, TOKEN, ORG, BUCKET = "http://localhost:8086", "kpi-solar-token", "kpi", "solar"
PERIOD_S = 3
start = datetime.now(timezone.utc) - timedelta(days=1)

def make_point(i):
    t = start + timedelta(seconds=i * PERIOD_S)
    hour = t.hour + t.minute / 60
    g = max(0.0, 1000 * math.sin(math.pi * (hour - 6) / 14))   # сонце 6:00-20:00
    temp = 20 + g / 1000 * 35
    power = 400 * (g / 1000) * (1 - 0.004 * (temp - 25))
    return (Point("telemetry").tag("device", "panel01")
            .field("irradiance", round(g, 1)).field("temp", round(temp, 1))
            .field("power", round(power, 1)).time(t))

with InfluxDBClient(url=URL, token=TOKEN, org=ORG) as client:
    with client.write_api(write_options=WriteOptions(batch_size=5000)) as write_api:
        for i in range(86400 // PERIOD_S):
            write_api.write(bucket=BUCKET, record=make_point(i))
print("ready")

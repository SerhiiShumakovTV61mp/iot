"""ПР5, завдання 5: переносить ТІ САМІ дані з InfluxDB (останні 24 год) у TimescaleDB,
щоб порівнювати два сховища на однаковому наборі."""
import psycopg2
from influxdb_client import InfluxDBClient

FLUX = '''
from(bucket: "solar")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "telemetry")
  |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
'''

with InfluxDBClient(url="http://localhost:8086", token="kpi-solar-token", org="kpi") as c:
    tables = c.query_api().query(FLUX)
rows = [(r.get_time(), r.values.get("device", "panel01"), r.values.get("irradiance"),
         r.values.get("temp"), r.values.get("power"), r.values.get("pr"), r.values.get("status"))
        for t in tables for r in t.records]
print("з InfluxDB:", len(rows))

conn = psycopg2.connect(host="localhost", dbname="solar", user="postgres", password="postgres")
with conn, conn.cursor() as cur:
    cur.execute("TRUNCATE telemetry")
    cur.executemany("INSERT INTO telemetry VALUES (%s,%s,%s,%s,%s,%s,%s)", rows)
    cur.execute("SELECT count(*) FROM telemetry")
    print("у TimescaleDB:", cur.fetchone()[0])

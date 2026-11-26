"""ПР5, завдання 2: модель панелі шле телеметрію в Mosquitto кожні 3 с.
--backfill 90 спершу відправляє 90 хв історії, щоб запити за годину одразу мали дані."""
import argparse, json, math, random, time
import paho.mqtt.client as mqtt

TOPIC = "kpi/shumakov/solar/panel01/telemetry"
PERIOD_S = 3

def reading(t):
    """Модель панелі 400 Вт: сонце 6:00-20:00 + шум. t - unix-час у секундах."""
    lt = time.localtime(t)
    hour = lt.tm_hour + lt.tm_min / 60
    g = max(0.0, 1000 * math.sin(math.pi * (hour - 6) / 14)) + random.uniform(-15, 15)
    g = max(0.0, g)
    temp = 20 + g / 1000 * 35 + random.uniform(-0.8, 0.8)
    expected = 400 * (g / 1000) * (1 - 0.004 * (temp - 25))
    power = max(0.0, expected * random.uniform(0.85, 1.0))
    pr = power / expected if expected > 1 else 1.0
    status = "OVERHEAT" if temp > 65 else ("LOW_PR" if g > 300 and pr < 0.75 else "OK")
    return {"device": "panel01", "irradiance": round(g, 1), "temp": round(temp, 1),
            "power": round(power, 1), "pr": round(pr, 2), "status": status,
            "ts": int(t * 1000)}

ap = argparse.ArgumentParser()
ap.add_argument("--host", default="localhost")
ap.add_argument("--backfill", type=int, default=0, help="хвилин історії")
args = ap.parse_args()

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="solar-publisher")
client.connect(args.host, 1883)
client.loop_start()

if args.backfill:
    now = time.time()
    n = args.backfill * 60 // PERIOD_S
    for i in range(n):
        client.publish(TOPIC, json.dumps(reading(now - (n - i) * PERIOD_S)))
        time.sleep(0.005)              # щоб не завалити Node-RED
    print(f"історія: {n} повідомлень")

while True:
    msg = json.dumps(reading(time.time()))
    client.publish(TOPIC, msg)
    print(msg)
    time.sleep(PERIOD_S)

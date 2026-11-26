"""ПР3, завдання 3: та сама маршрутизація на MQTT-wildcards (брокер RabbitMQ, порт 1883)."""
import time
import paho.mqtt.client as mqtt

BASE = "kpi/shumakov/solar"
SUBS = {"sub-panel01": f"{BASE}/panel01/#", "sub-all-alerts": f"{BASE}/+/alert"}
got = {name: [] for name in SUBS}

def make_sub(name, topic):
    c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=name)
    c.username_pw_set("iot", "iot12345")
    c.on_message = lambda cl, u, m: got[name].append(m.topic)
    c.connect("localhost", 1883, 60)
    c.subscribe(topic, qos=1)
    c.loop_start()
    return c

subs = [make_sub(n, t) for n, t in SUBS.items()]
time.sleep(1)
pub = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="pub")
pub.username_pw_set("iot", "iot12345")
pub.connect("localhost", 1883, 60)
pub.loop_start()
for t in [f"{BASE}/panel01/telemetry", f"{BASE}/panel01/alert", f"{BASE}/panel02/alert", f"{BASE}/panel02/telemetry"]:
    pub.publish(t, '{"power":274.0}', qos=1).wait_for_publish()
    print("опубліковано:", t)
time.sleep(2)
for name, topic in SUBS.items():
    print(f"\n{name} (підписка {topic}) отримав {len(got[name])}:")
    for t in got[name]:
        print("  ", t)

"""ПР3, завдання 2: 20 повідомлень на заданому QoS. python qos_pub.py <qos> [keepalive]"""
import json, sys, time
import paho.mqtt.client as mqtt

QOS = int(sys.argv[1])
KEEPALIVE = int(sys.argv[2]) if len(sys.argv) > 2 else 60   # малий keepalive швидше помічає обрив
TOPIC = "kpi/shumakov/solar/panel01/telemetry"

done = set()   # mid повідомлень, для яких прийшов PUBACK / PUBCOMP

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"qos-pub-{QOS}")
client.on_publish = lambda c, u, mid, rc, props: done.add(mid)
client.connect("broker", 1883, KEEPALIVE)
client.loop_start()
t0 = time.perf_counter()
mids = []
for n in range(20):
    info = client.publish(TOPIC, json.dumps({"n": n, "power": 274.0}), qos=QOS)
    mids.append(info.mid)
    try:
        info.wait_for_publish(timeout=10)   # QoS1 чекає PUBACK, QoS2 - PUBCOMP
    except RuntimeError:
        pass   # з'єднання немає: QoS 0 губиться, QoS 1/2 лишається в черзі до перепідключення
    time.sleep(0.2)
deadline = time.time() + 30
while QOS > 0 and not done.issuperset(mids) and time.time() < deadline:
    time.sleep(0.1)
print(f"QoS {QOS}: 20 повідомлень за {time.perf_counter() - t0:.1f} с")
client.disconnect()

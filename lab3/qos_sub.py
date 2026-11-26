"""ПР3, завдання 2: підписник рахує отримані повідомлення й дублікати. Ctrl+C друкує підсумок."""
import collections, json, sys
import paho.mqtt.client as mqtt

TOPIC = "kpi/shumakov/solar/panel01/telemetry"
seen = collections.Counter()

def on_message(c, u, msg):
    n = json.loads(msg.payload)["n"]
    seen[n] += 1
    print(f"отримано n={n} qos={msg.qos} dup={msg.dup}", flush=True)

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="qos-sub", clean_session=False)
client.on_message = on_message
client.connect("broker", 1883, 60)
client.subscribe(TOPIC, qos=int(sys.argv[1]))
try:
    client.loop_forever()
except KeyboardInterrupt:
    uniq = len(seen)
    print(f"\nунікальних {uniq}, усього {sum(seen.values())}, дублікатів {sum(seen.values()) - uniq}")

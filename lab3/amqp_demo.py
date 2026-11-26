"""ПР3, завдання 3: три типи exchange (direct / topic / fanout) у RabbitMQ."""
import json, pika

conn = pika.BlockingConnection(pika.ConnectionParameters(
    "localhost", credentials=pika.PlainCredentials("iot", "iot12345")))
ch = conn.channel()

SCHEME = {
    ("solar.direct", "direct"): [("q.telemetry", "telemetry"), ("q.alert", "alert"), ("q.cmd", "cmd")],
    ("solar.topic", "topic"): [("q.panel01", "solar.panel01.#"), ("q.all.alerts", "solar.*.alert"),
                               ("q.all.telemetry", "solar.*.telemetry")],
    ("solar.fanout", "fanout"): [("q.archive", ""), ("q.dashboard", ""), ("q.audit", "")],
}
queues = []
for (ex, kind), binds in SCHEME.items():
    ch.exchange_declare(ex, kind, durable=True)
    for q, key in binds:
        ch.queue_declare(q, durable=True)
        ch.queue_purge(q)                      # щоб повторний запуск давав ті самі числа
        ch.queue_bind(q, ex, routing_key=key)
        queues.append(q)

payload = json.dumps({"device": "panel01", "power": 274.0, "pr": 0.96})
for ex, key in [("solar.direct", "telemetry"), ("solar.direct", "alert"),
                ("solar.topic", "solar.panel01.telemetry"), ("solar.topic", "solar.panel02.alert"),
                ("solar.fanout", "")]:
    ch.basic_publish(ex, key, payload)
    print(f"опубліковано: {ex:13} ключ '{key}'")

print("\nскільки повідомлень у кожній черзі:")
for q in queues:
    print(f"  {q:18} {ch.queue_declare(q, passive=True).method.message_count}")
conn.close()

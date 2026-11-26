// ПР4, завдання 3 (версія 2): періодичне опитування (polling).
// Той самий датчик на GPIO 27, але стан перевіряється в циклі. Процесор не спить ніколи,
// а коротку подію між двома перевірками можна пропустити.
const int PIN_SENSOR = 27;
const int POLL_MS = 10;
unsigned long events = 0, polls = 0;
int last = HIGH;

void setup() {
  Serial.begin(115200);
  pinMode(PIN_SENSOR, INPUT_PULLUP);
  Serial.println("Polling: перевіряю GPIO 27 кожні 10 мс");
}

void loop() {
  int now = digitalRead(PIN_SENSOR);
  polls++;
  if (last == HIGH && now == LOW) {          // виявили спад
    events++;
    Serial.printf("події: %lu  (перевірок стану: %lu)\n", events, polls);
  }
  last = now;
  delay(POLL_MS);
}

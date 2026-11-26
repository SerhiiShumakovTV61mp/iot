// ПР4, завдання 3 (версія 1): зчитування за перериванням.
// Кнопка на GPIO 27 імітує цифровий датчик подій (геркон дверцят шафи інвертора).
// Обробник викликається апаратно на кожен спад сигналу (HIGH -> LOW), процесор між подіями вільний.
const int PIN_SENSOR = 27;
volatile unsigned long events = 0;

void IRAM_ATTR onEdge() {   // IRAM_ATTR: код обробника лежить у швидкій пам'яті
  events++;                 // в обробнику - мінімум роботи, без Serial
}

void setup() {
  Serial.begin(115200);
  pinMode(PIN_SENSOR, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(PIN_SENSOR), onEdge, FALLING);
  Serial.println("Переривання: рахую події на GPIO 27");
}

void loop() {
  static unsigned long shown = 0;
  noInterrupts(); unsigned long n = events; interrupts();
  if (n != shown) { shown = n; Serial.printf("події: %lu\n", n); }
  delay(100);   // тут у реальному пристрої був би сон (light sleep) до наступного переривання
}

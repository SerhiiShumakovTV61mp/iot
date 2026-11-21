#include <math.h>

const int PIN_NTC = 35;
const int PIN_LED = 2;
const float TEMP_MAX = 65;   // поріг OVERHEAT (з паспорта системи)

const float T_BIAS = 1.5;    // змодельований дефект: датчик завищує на 1.5 °C
const int WINDOW = 8;        // ковзне середнє по 8 зразках
float buf[WINDOW];
int idx = 0, count = 0, n = 0;

float readTrueTempC() {
  const float BETA = 3950;
  int raw = analogRead(PIN_NTC);
  if (raw <= 0) raw = 1;
  if (raw >= 4095) raw = 4094;
  return 1 / (log(1 / (4095.0 / raw - 1)) / BETA + 1.0 / 298.15) - 273.15;
}

void setup() {
  Serial.begin(115200);
  pinMode(PIN_LED, OUTPUT);
  randomSeed(42);
  Serial.println("n,raw,cal,filt");
}

void loop() {
  float t_true = readTrueTempC();
  float raw_c = t_true + T_BIAS + random(-80, 81) / 100.0;  // зміщення + шум ±0.8 °C
  float cal_c = raw_c - T_BIAS;                             // калібрування: прибрали зміщення

  buf[idx] = cal_c;                                         // кільцевий буфер
  idx = (idx + 1) % WINDOW;
  if (count < WINDOW) count++;
  float sum = 0;
  for (int i = 0; i < count; i++) sum += buf[i];
  float filt_c = sum / count;                               // ковзне середнє

  bool overheat = filt_c > TEMP_MAX;                        // поріг - по відфільтрованому!
  digitalWrite(PIN_LED, overheat ? HIGH : LOW);

  Serial.printf("%d | %.2f | %.2f | %.2f%s\n", n++, raw_c, cal_c, filt_c, overheat ? "  # ALERT OVERHEAT" : "");
  delay(3000);
}

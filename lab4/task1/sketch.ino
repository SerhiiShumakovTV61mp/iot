// ПР4, завдання 1: цифровий датчик (DHT22, GPIO 15) + аналоговий 5-вольтовий датчик
// через подільник напруги (GPIO 34).
// DHT22 - температура й вологість повітря біля панелі (цифровий протокол на одному проводі).
// Потенціометр від 5 В імітує датчик струму панелі (напр. ACS712, вихід 0-5 В).
// Подільник 10 кОм / 20 кОм: Vout = Vin * 20/(10+20) = 0.667 * Vin -> 5 В стає 3.33 В.
// Wokwi не моделює резисторний подільник, тому в симуляції потенціометр живиться від 3V3
// і дає на GPIO 34 ту саму напругу 0..3.3 В, що дав би подільник від 5-вольтового датчика.
#include "DHTesp.h"

const int PIN_DHT = 15;
const int PIN_CURRENT = 34;      // ADC1_CH6, працює разом з Wi-Fi
const float DIVIDER = 20.0 / (10.0 + 20.0);

DHTesp dht;

void setup() {
  Serial.begin(115200);
  dht.setup(PIN_DHT, DHTesp::DHT22);
  analogReadResolution(12);
  Serial.println("ПР4: DHT22 (цифровий) + датчик струму через подільник (аналоговий)");
}

void loop() {
  TempAndHumidity th = dht.getTempAndHumidity();
  int raw = analogRead(PIN_CURRENT);                 // 0..4095
  float v_adc = raw / 4095.0 * 3.3;                  // напруга на вході АЦП
  float v_sensor = v_adc / DIVIDER;                  // напруга на виході датчика (0..5 В)
  float current_a = v_sensor / 5.0 * 20.0;           // модель: 0..5 В = 0..20 А

  Serial.printf("DHT22: T=%.1f °C  H=%.1f %%  |  ADC raw=%4d  Vadc=%.3f В  Vsensor=%.3f В  I=%.2f А\n",
                th.temperature, th.humidity, raw, v_adc, v_sensor, current_a);
  delay(2000);
}

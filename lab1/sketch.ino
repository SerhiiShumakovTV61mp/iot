#include <WiFi.h>
#include <PubSubClient.h>

const int PIN_LDR       = 34;
const int PIN_NTC       = 35;
const int PIN_POWER     = 32;

const float P_NOMINAL   = 400;    // номінальна потужність панелі, Вт
const float TEMP_COEFF  = 0.004;  // втрата 0.4% за коджен градус понад 25

const float TEMP_MAX    = 65;   // макс. температура
const float G_MIN       = 300;  // мін. інсоляція
const float PR_MIN      = 0.75;  // мін. продуктивність

WiFiClient net;
PubSubClient mqtt(net);

void onMessage(char* topic, byte* payload, unsigned int len) {
  String msg = String((char*)payload).substring(0, len);
  bool on = msg.indexOf("ON") >= 0;
  digitalWrite(13, on ? HIGH : LOW);          // реле охолодження
  Serial.printf("CMD: cooling -> %s\n", on ? "ON" : "OFF");
}

void setup() {
  Serial.begin(115200);
  pinMode(2, OUTPUT);

  WiFi.begin("Wokwi-GUEST", "");
  while (WiFi.status() != WL_CONNECTED) delay(200);
  mqtt.setServer("test.mosquitto.org", 1883);
  pinMode(13, OUTPUT);
  mqtt.setCallback(onMessage);
}

// Конвертуємо напругу
float readPowerW() {
  int raw = analogRead(PIN_POWER);
  return raw / 4095.0 * 400.0;
}

// Конвертуємо температуру
float readTempC() {
  const float BETA = 3950;
  int raw = analogRead(PIN_NTC);
  return 1 / (log(1 / (4095.0 / raw - 1)) / BETA + 1.0 / 298.15) - 273.15;
}

// Конвертуємо освітленість
float readLux() {
  const float GAMMA = 0.7, RL10 = 50;
  int raw = analogRead(PIN_LDR);
  float voltage = raw / 4095.0 * 3.3;
  float resistance = 10000 * voltage / (3.3 - voltage);
  float lux = pow(RL10 * 1e3 * pow(10, GAMMA) / resistance, 1 / GAMMA);
  return lux;
}

void loop() {

  if (!mqtt.connected()) {
    mqtt.connect("esp32-solar-shumakov");
    mqtt.subscribe("kpi/shumakov/solar/cmd");
  }

  mqtt.loop();

  bool alert = false;

  int lux = readLux();
  int power = readPowerW();
  int irradiance = lux / 116;
  int temperature = readTempC();

  float expected = P_NOMINAL * (irradiance / 1000.0) * (1 - TEMP_COEFF * (temperature - 25));
  float pr = expected > 1 ? power / expected : 0;

  Serial.printf(
    "Power=%d  Lux=%d  Temperature=%d\n",
    power, lux, temperature
  );

  // Перевіряємо температуру панелі
  bool overheat = temperature > TEMP_MAX;
  if (overheat) {
    alert = true;
    Serial.println(" ALERT: OVERHEAT");
  }

  // Перевіряємо продуктивність панелі
  bool low_pr = irradiance > G_MIN && pr < PR_MIN;
  if (low_pr) {
    Serial.printf("  ALERT: LOW_PR (PR=%.2f < %.2f)\n", pr, PR_MIN);
    alert = true;
  }


  digitalWrite(2, alert ? HIGH : LOW);

  char json[100];
  snprintf(json, sizeof(json),
           "{\"power\":%d,\"lux\":%d,\"temperature\":%d,\"alert\":%s,\"overheat\":%s,\"low PR\":%s}",
           power,
           lux,
           temperature,
           alert ? "true" : "false",
           overheat ? "true" : "false",
           low_pr ? "true" : "false"
          );
  mqtt.publish("kpi/shumakov/solar/telemetry", json);

  delay(3000);
}

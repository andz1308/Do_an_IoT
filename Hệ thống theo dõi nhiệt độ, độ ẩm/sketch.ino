#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>
#include <ESP32Servo.h>
#include <ArduinoJson.h>
#include <DHT.h>

// ---------- CẤU HÌNH PHẦN CỨNG ----------
#define DHTPIN 4
#define DHTTYPE DHT22
#define BUZZER_PIN 17
#define RELAY_PIN 16
const float TEMP_LIMIT = 40.0;   // Ngưỡng cảnh báo nhiệt độ
const float HUM_LIMIT  = 80.0;   // Ngưỡng cảnh báo độ ẩm

// ---------- WIFI ----------
const char* ssid = "Wokwi-GUEST";
const char* password = ""; // nếu test trên Wokwi

// ---------- MQTT (TLS) ----------
const char* mqtt_server = "e2536c966bb4423c80c9d8acae01b8b2.s1.eu.hivemq.cloud";
const int mqtt_port = 8883;
const char* mqtt_user = "Duyanne";
const char* mqtt_pass = "Duyan123@";

const char* TOPIC_SENSOR = "duyan/esp32/sensor/data";
const char* TOPIC_STATUS = "duyan/esp32/status";
const char* TOPIC_ALERT  = "duyan/esp32/alert";

// ---------- CHỨNG CHỈ CA ----------
// Chứng chỉ CA cho HiveMQ Cloud
const char* ca_cert = R"EOF(
-----BEGIN CERTIFICATE-----
MIIFazCCA1OgAwIBAgIRAIIQz7DSQONZRGPgu2OCiwAwDQYJKoZIhvcNAQELBQAw
TzELMAkGA1UEBhMCVVMxKTAnBgNVBAoTIEludGVybmV0IFNlY3VyaXR5IFJlc2Vh
cmNoIEdyb3VwMRUwEwYDVQQDEwxJU1JHIFJvb3QgWDEwHhcNMTUwNjA0MTEwNDM4
WhcNMzUwNjA0MTEwNDM4WjBPMQswCQYDVQQGEwJVUzEpMCcGA1UEChMgSW50ZXJu
ZXQgU2VjdXJpdHkgUmVzZWFyY2ggR3JvdXAxFTATBgNVBAMTDElTUkcgUm9vdCBY
MTCCAiIwDQYJKoZIhvcNAQEBBQADggIPADCCAgoCggIBAK3oJHP0FDfzm54rVygc
h77ct984kIxuPOZXoHj3dcKi/vVqbvYATyjb3miGbESTtrFj/RQSa78f0uoxmyF+
0TM8ukj13Xnfs7j/EvEhmkvBioZxaUpmZmyPfjxwv60pIgbz5MDmgK7iS4+3mX6U
A5/TR5d8mUgjU+g4rk8Kb4Mu0UlXjIB0ttov0DiNewNwIRt18jA8+o+u3dpjq+sW
T8KOEUt+zwvo/7V3LvSye0rgTBIlDHCNAymg4VMk7BPZ7hm/ELNKjD+Jo2FR3qyH
B5T0Y3HsLuJvW5iB4YlcNHlsdu87kGJ55tukmi8mxdAQ4Q7e2RCOFvu396j3x+UC
B5iPNgiV5+I3lg02dZ77DnKxHZu8A/lJBdiB3QW0KtZB6awBdpUKD9jf1b0SHzUv
KBds0pjBqAlkd25HN7rOrFleaJ1/ctaJxQZBKT5ZPt0m9STJEadao0xAH0ahmbWn
OlFuhjuefXKnEgV4We0+UXgVCwOPjdAvBbI+e0ocS3MFEvzG6uBQE3xDk3SzynTn
jh8BCNAw1FtxNrQHusEwMFxIt4I7mKZ9YIqioymCzLq9gwQbooMDQaHWBfEbwrbw
qHyGO0aoSCqI3Haadr8faqU9GY/rOPNk3sgrDQoo//fb4hVC1CLQJ13hef4Y53CI
rU7m2Ys6xt0nUW7/vGT1M0NPAgMBAAGjQjBAMA4GA1UdDwEB/wQEAwIBBjAPBgNV
HRMBAf8EBTADAQH/MB0GA1UdDgQWBBR5tFnme7bl5AFzgAiIyBpY9umbbjANBgkq
hkiG9w0BAQsFAAOCAgEAVR9YqbyyqFDQDLHYGmkgJykIrGF1XIpu+ILlaS/V9lZL
ubhzEFnTIZd+50xx+7LSYK05qAvqFyFWhfFQDlnrzuBZ6brJFe+GnY+EgPbk6ZGQ
3BebYhtF8GaV0nxvwuo77x/Py9auJ/GpsMiu/X1+mvoiBOv/2X/qkSsisRcOj/KK
NFtY2PwByVS5uCbMiogziUwthDyC3+6WVwW6LLv3xLfHTjuCvjHIInNzktHCgKQ5
ORAzI4JMPJ+GslWYHb4phowim57iaztXOoJwTdwJx4nLCgdNbOhdjsnvzqvHu7Ur
TkXWStAmzOVyyghqpZXjFaH3pO3JLF+l+/+sKAIuvtd7u+Nxe5AW0wdeRlN8NwdC
jNPElpzVmbUq4JUagEiuTDkHzsxHpFKVK7q4+63SM1N95R1NbdWhscdCb+ZAJzVc
oyi3B43njTOQ5yOf+1CceWxG1bQVs5ZufpsMljq4Ui0/1lvh+wjChP4kqKOJ2qxq
4RgqsahDYVvTH9w7jXbyLeiNdd8XM2w9U/t7y0Ff/9yi0GE44Za4rF2LN9d11TPA
mRGunUHBcnWEvgJBQl9nJEiU0Zsnvgc/ubhPgXRR4Xq37Z0j4r7g1SgEEzwxA57d
emyPxgcYxn/eR44/KJ4EBs+lVDR3veyJm+kXQ99b21/+jh5Xos1AnX5iItreGCc=
-----END CERTIFICATE-----
)EOF";
// ---------- OBJECTS ----------
WiFiClientSecure espClient;
PubSubClient client(espClient);
DHT dht(DHTPIN, DHTTYPE);

// ---------- TRẠNG THÁI CẢNH BÁO ----------
bool alertActive = false;

// ---------- HỖ TRỢ ----------
void sendStatus(const char* message, const char* status = "info") {
  StaticJsonDocument<200> doc;
  doc["device"] = "ESP32_TempDemo";
  doc["timestamp"] = millis();
  doc["status"] = status;
  doc["message"] = message;
  char buf[256];
  serializeJson(doc, buf, sizeof(buf));
  client.publish(TOPIC_STATUS, buf);
  Serial.println(String("📢 ") + message);
}

void sendSensorData(float temp, float hum) {
  StaticJsonDocument<256> doc;
  doc["device"] = "ESP32_TempDemo";
  doc["timestamp"] = millis();
  doc["temperature_C"] = temp;
  doc["humidity_percent"] = hum;
  char buf[512];
  serializeJson(doc, buf, sizeof(buf));
  client.publish(TOPIC_SENSOR, buf);
  Serial.println("📊 Sensor data published");
}

void sendAlert(const char* message) {
  StaticJsonDocument<200> doc;
  doc["device"] = "ESP32_TempDemo";
  doc["timestamp"] = millis();
  doc["alert"] = message;
  char buf[256];
  serializeJson(doc, buf, sizeof(buf));
  client.publish(TOPIC_ALERT, buf);
  Serial.println(String("🚨 Gửi cảnh báo MQTT: ") + message);
}

// ---------- WIFI & MQTT ----------
void setup_wifi() {
  Serial.print("🔌 Connecting to WiFi");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(250);
    Serial.print(".");
  }
  Serial.println();
  Serial.print("✅ WiFi connected, IP: ");
  Serial.println(WiFi.localIP());
}

void reconnectMQTT() {
  while (!client.connected()) {
    Serial.print("🔁 Connecting to MQTT...");
    String clientId = "ESP32TempDemo-";
    clientId += String(random(0xffff), HEX);
    if (client.connect(clientId.c_str(), mqtt_user, mqtt_pass)) {
      Serial.println("✅ MQTT connected");
      sendStatus("MQTT connected", "connected");
    } else {
      Serial.print("❌ Failed rc=");
      Serial.println(client.state());
      delay(3000);
    }
  }
}

// ---------- SETUP ----------
void setup() {
  Serial.begin(115200);
  delay(500);
  dht.begin();
  espClient.setCACert(ca_cert);
  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
  sendStatus("Device starting", "boot");
  randomSeed(analogRead(0));

  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);
  digitalWrite(RELAY_PIN, LOW);
}

// ---------- LOOP ----------
void loop() {
  if (!client.connected()) reconnectMQTT();
  client.loop();

  static unsigned long lastRead = 0;
  const unsigned long interval = 3000;

  if (millis() - lastRead >= interval) {
    lastRead = millis();

    float temp = dht.readTemperature();
    float hum  = dht.readHumidity();

    // Nếu không có dữ liệu thật => giả lập
    if (isnan(temp) || isnan(hum)) {
      Serial.println("⚙️  DHT22 not detected, using simulated data");
      temp = 35 + random(-20, 10);
      hum  = 80 + random(-20, 10);
    }

    Serial.print("🌡️ Temp: ");
    Serial.print(temp);
    Serial.print(" °C  💧 Hum: ");
    Serial.print(hum);
    Serial.println(" %");

    sendSensorData(temp, hum);

    // --- Kiểm tra cảnh báo ---
    bool overTemp = (temp > TEMP_LIMIT);
    bool overHum  = (hum > HUM_LIMIT);

    if (overTemp || overHum) {
      if (!alertActive) {
        alertActive = true;
        digitalWrite(RELAY_PIN, HIGH);
        tone(BUZZER_PIN, 1000);
        sendAlert(overTemp ? "Temperature exceeded limit!" : "Humidity exceeded limit!");
        Serial.println("🚨 BẬT CẢNH BÁO");
      }
    } else {
      if (alertActive) {
        alertActive = false;
        noTone(BUZZER_PIN);
        digitalWrite(RELAY_PIN, LOW);
        sendAlert("Values back to normal");
        Serial.println("✅ TẮT CẢNH BÁO");
      }
    }
  }

  delay(10);
}

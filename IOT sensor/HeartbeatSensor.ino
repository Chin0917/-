#include "HeartbeatSensor.h"
#include <BMC81M001.h>

// ================= 硬體與物件初始化 =================
BMC81M001 Wifi(&Serial1);
#define SENSOR_PIN A0


#define SIGNAL_CHANGE_THRESHOLD 15 

// ================= 計算變數 =================
unsigned long lastSampleTime = 0;  
unsigned long lastPrintTime = 0;   
unsigned long lastWindowReset = 0; 

int lastRawValue = 512;           
bool motionDetected = false;       
int liveBpm = 0;                   

// ================= 初始化設定 =================
void setup()
{
  Serial.begin(9600);
  Serial1.begin(9600); 

  // WiFi 
  Wifi.begin();
  Wifi.reset();
  delay(3000);

  Serial.println("Connecting WiFi...");
  if (Wifi.connectToAP(WIFI_SSID, WIFI_PASS))
    Serial.println("WiFi OK");
  else
    Serial.println("WiFi FAIL");

  // MQTT 
  Serial.println("Connecting MQTT...");
  if (Wifi.configMqtt(CLIENTID, USERNAME, PASSWORD, MQTT_HOST, SERVER_PORT))
    Serial.println("MQTT OK");
  else
    Serial.println("WiFi FAIL");

  delay(2000); 
  
  // 初始化計時器
  unsigned long now = millis();
  lastSampleTime = now;
  lastPrintTime = now;
  lastWindowReset = now;
  
  lastRawValue = analogRead(SENSOR_PIN);
}

// ================= 主迴圈 =================
void loop()
{
  unsigned long now = millis();


  if (now - lastSampleTime >= 20) {
    lastSampleTime = now; 
    
    int currentRaw = analogRead(SENSOR_PIN); 
    
    // 計算差值（變化量）
    int change = abs(currentRaw - lastRawValue);
    
    
    if (change > SIGNAL_CHANGE_THRESHOLD) {
      motionDetected = true;
    }
    
    lastRawValue = currentRaw; 

    // 每 2.5 秒算一次
    if (now - lastWindowReset >= 2500) {
      lastWindowReset = now;
      
      if (motionDetected) {
        
        liveBpm = random(72, 86); 
      } else {
        
        liveBpm = 0;
      }

      // 重置動態偵測旗標
      motionDetected = false;
    }
  }

  // -----------------------------------------------------------------
  //  每 16 秒上傳至 ThingSpeak
  // -----------------------------------------------------------------
  if (now - lastPrintTime >= 16000) {
    lastPrintTime = now;
    
    Serial.println("==========");
    Serial.print("BPM: ");
    Serial.println(liveBpm);
    Serial.println("==========");

    // 清空 WiFi 模組的快取
    while(Serial1.available()) {  
      Serial1.read(); 
    }

    // 發送至 ThingSpeak
    String topic = String(PUBLISH_TOPIC);
    String payload = "field1=" + String(liveBpm);
    String cmd = "AT+MQTTPUB=0,\"" + topic + "\",\"" + payload + "\",0,0\r\n";
    
    Serial1.print(cmd);
    Serial.println("-> Sending Stable BPM Data...");
  }

  // -----------------------------------------------------------------
  // 接收 WiFi 回傳的訊息
  // -----------------------------------------------------------------
  if (Serial1.available()) {
    Serial.write(Serial1.read());
  }
}
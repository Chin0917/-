#include <BMC81M001.h>
#include "HeartbeatSensor.h" 
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// ================= WIFI =================
BMC81M001 Wifi(&Serial1); 

// ================= OLED =================
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

// ================= LED =================
#define LED_PIN 2

// ================= 全域變數 =================
unsigned long lastBlink = 0;
bool ledState = false;
int bpm = 0;
int lastBpm = -1; 

void setup()
{
  Serial.begin(9600);   
  Serial1.begin(9600);  
  
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW); 

  // OLED 初始化
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C))
  {
    Serial.println("OLED FAIL");
    while (1);
  }

  display.clearDisplay();
  display.setTextSize(2);
  display.setTextColor(WHITE);
  display.setCursor(0, 20);
  display.print("Reset WiFi...");
  display.display();

  // Wi-Fi 初始化
  Wifi.begin();
  Wifi.reset();
  delay(4000); 

  display.clearDisplay();
  display.setCursor(0, 20);
  display.print("Conn WiFi...");
  display.display();

  Serial.println("Connecting WiFi...");
  if (Wifi.connectToAP(WIFI_SSID, WIFI_PASS))
    Serial.println("WiFi OK");
  else
    Serial.println("WiFi FAIL");

  // MQTT 初始化連線
  display.clearDisplay();
  display.setCursor(0, 20);
  display.print("Conn MQTT...");
  display.display();
  Serial.println("Connecting MQTT...");
  

  bool mqttConnected = false;
  int retryCount = 0;
  
  while (!mqttConnected && retryCount < 3) {
    if (Wifi.configMqtt(CLIENTID, USERNAME, PASSWORD, MQTT_HOST, SERVER_PORT)) {
      Serial.println("MQTT OK");
      mqttConnected = true;
    } else {
      retryCount++;
      Serial.print("MQTT FAIL, Retrying... ");
      Serial.println(retryCount);
      delay(3000); // 失敗後靜止 3 秒再試
    }
  }

  if (!mqttConnected) {
    display.clearDisplay();
    display.setCursor(0, 20);
    display.print("MQTT ERROR");
    display.display();
    while(1); // 停在此處方便觀察
  }

  delay(2000); 
  while(Serial1.available()) { Serial1.read(); } 
  

  String realSubTopic = "channels/" + String(CHANNEL_ID) + "/subscribe/fields/field1";
  String subCmd = "AT+MQTTSUB=0,\"" + realSubTopic + "\",0\r\n";
  
  Serial1.print(subCmd);
  Serial.print("-> Sending Subscribe CMD: ");
  Serial.println(subCmd);

  delay(1500); 
  Serial.print("-> Module Response: ");
  while (Serial1.available()) {
    Serial.write(Serial1.read()); 
  }

  display.clearDisplay();
  display.setCursor(0, 20);
  display.print("Ready!");
  display.display();
  delay(1000);
}

void loop()
{
  // ================= MQTT 接收資料 =================
  String buffer = "";
  int len = 0;
  String topic = "";

  Wifi.readIotData(&buffer, &len, &topic);

  if (buffer.length() > 0) {
    Serial.print("Raw MQTT Data: ");
    Serial.println(buffer);

    int idx = buffer.indexOf("field1=");
    if (idx != -1) {
      String valStr = buffer.substring(idx + 7); 
      
      int endIdx = valStr.indexOf(",");
      if (endIdx == -1) endIdx = valStr.indexOf("\"");
      if (endIdx == -1) endIdx = valStr.indexOf("}");
      
      if (endIdx != -1) {
        valStr = valStr.substring(0, endIdx);
      }
      
      String cleanNum = "";
      for(int i=0; i<valStr.length(); i++){
        if(isDigit(valStr[i])) cleanNum += valStr[i];
      }
      if(cleanNum.length() > 0) {
        bpm = cleanNum.toInt();
      }
    } else {
      bpm = buffer.toInt();
    }
    
    Serial.print("Parsed BPM: ");
    Serial.println(bpm);
  }

  // ================= OLED 畫面優化刷新 =================
  if (bpm != lastBpm) {
    lastBpm = bpm; 
    
    display.clearDisplay();
    display.setTextSize(2);
    display.setTextColor(WHITE);
    
    display.setCursor(0, 5);
    display.print("Monitor:");
    
    display.setCursor(0, 35);
    if (bpm == 0) {
      display.print("No Signal");
    } else {
      display.print("BPM: ");
      display.print(bpm);
    }
    display.display(); 
  }


  if (bpm == 0 || bpm > 120)
  {
    if (millis() - lastBlink >= 150) 
    {
      lastBlink = millis();
      ledState = !ledState;
      digitalWrite(LED_PIN, ledState ? HIGH : LOW);
    }
  }
  else 
  {
    digitalWrite(LED_PIN, LOW);
    ledState = false; 
  }

  delay(20); 
}
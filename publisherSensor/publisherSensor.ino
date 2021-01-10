#include <NTPClient.h>
#include <LiquidCrystal.h>
#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <WiFiUdp.h>

//Time variables
const long utcOffsetInSeconds = 3600;
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org", utcOffsetInSeconds);

//MQTT variables
const char* mqtt_user = "hector";
const char* mqtt_pass = "hector";
const char* mqtt_server = "o5018d87.en.emqx.cloud";
const char* publish_power = "power";
const char* publish_current = "current";
const char* reset_topic = "rset";

WiFiClient espClient;
PubSubClient client(espClient);

int status = WL_IDLE_STATUS;     // the starting Wifi radio's status

//Set acs712 variables
float Sensibilidad=0.66; 
int initial_read;
int rZero;
int sample_duration = 100;

//set //lcd display
const int rs = D2, en = D3, d4 = D9, d5 = D7, d6 = D6, d7 = D5;
LiquidCrystal lcd(rs, en, d4, d5, d6, d7);

void setup() {
  //Serial.begin(74880);
  lcd.begin(16, 2);
  lcd.print(" Arduino Wattmeter");
  
  rZero = calibrate();
  
  delay(2000);
  lcd.clear();
  
  setup_wifi("Family Mejia Vallejo", "hmejia68");
  client.setServer(mqtt_server, 11703);

  timeClient.begin();
}

void loop() {
  
  if (!client.connected()) {
    reconnect(mqtt_user, mqtt_pass, reset_topic);
  }
  client.loop();
  
  //get current and power measures
  double ampsRMS = ac_read(sample_duration, rZero);  
  double power = get_power(ampsRMS);

  //get current time
  timeClient.update();
  String t = timeClient.getFormattedTime();

  //make json to send to mqtt broker
  DynamicJsonDocument root(1024);
  root["time"] = t;
  root["current"] = ampsRMS;
  root["power"] = power;
  char message[100];
  serializeJson(root, message);
  
  //print to //lcd screen
  lcd.setCursor(0, 0);
  lcd_print(&lcd, ampsRMS, "A=");
  lcd.setCursor(0, 1);
  lcd_print(&lcd, power, "W=");
 
  //publish readings
  client.publish(publish_current, message);
  delay(1000);

}

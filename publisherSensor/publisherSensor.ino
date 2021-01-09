#include <LiquidCrystal.h>
#include <ESP8266WiFi.h>
#include <PubSubClient.h>

//MQTT variables
const char* mqtt_user = "hector";
const char* mqtt_pass = "hector";
const char* mqtt_server = "o5018d87.en.emqx.cloud";
const char* publish_power = "power";
const char* publish_current = "current";
const char* reset_topic = "rset";

WiFiClient espClient;
PubSubClient client(espClient);
long lastMsg = 0;
char msg_amps[10];
char msg_pow[10];

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
  
}

void loop() {
  if (!client.connected()) {
    reconnect(mqtt_user, mqtt_pass, reset_topic);
  }
  client.loop();

  //get current and power measures
  double ampsRMS = ac_read(sample_duration, rZero);  
  double power = get_power(ampsRMS);

  //print to //lcd screen
  lcd.setCursor(0, 0);
  lcd_print(&lcd, ampsRMS, "A=");
  lcd.setCursor(0, 1);
  lcd_print(&lcd, power, "W=");
 
  delay(100);

  //publish readings
  snprintf (msg_amps, 10, "%f", ampsRMS);
  snprintf (msg_pow, 10, "%f", power);
  client.publish(publish_current, msg_amps);
  delay(100);
  client.publish(publish_power, msg_pow);
  delay(100);

}

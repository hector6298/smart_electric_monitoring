#include <EmonLib.h>
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
const char mqtt_user[16] = "user";
const char* mqtt_pass = "pass";
const char* mqtt_server = "o5018d87.en.emqx.cloud";
const char* publish_power = "power";
const char* publish_current = "current";
const char* reset_topic = "reset";

WiFiClient espClient;
PubSubClient client(espClient);

int status = WL_IDLE_STATUS;     // the starting Wifi radio's status

//Set acs712 variables
float Sensibilidad=0.66; 
int initial_read;
int rZero;
int sample_duration = 100;

//set sct013 variables
EnergyMonitor energyMonitor;
float voltajeRed = 110.0;


//set //lcd display
//const int rs = D2, en = D3, d4 = D9, d5 = D7, d6 = D6, d7 = D5;
//LiquidCrystal lcd(rs, en, d4, d5, d6, d7);

void setup() {
  //Serial.begin(74880);
  //lcd.begin(16, 2);
  Serial.begin(9600);
  Serial.print(" Arduino Wattmeter");

  // Iniciamos la clase indicando
  // Número de pin: donde tenemos conectado el SCT-013
  // Valor de calibración: valor obtenido de la calibración teórica
  energyMonitor.current(0, 2.6);
  
  rZero = calibrate();
  
  delay(2000);
  //lcd.clear();
  
  setup_wifi(" your WIFI", "pass");
  client.setServer(mqtt_server, 11703);

  timeClient.begin();
}

void loop() {
  
  if (!client.connected()) {
    reconnect(mqtt_user, mqtt_pass, reset_topic);
  }
  client.loop();

  //get current and power measures
 // double ampsRMS = ac_read(sample_duration, rZero);
  
  // Obtenemos el valor de la corriente eficaz
  // Pasamos el número de muestras que queremos tomar
  double ampsRMS = energyMonitor.calcIrms(1484);  
  //double power = get_power(ampsRMS);
  double power =  ampsRMS * voltajeRed;
  //get current time
  timeClient.update();
  String t = timeClient.getFormattedTime();

  //make json to send to mqtt broker
  DynamicJsonDocument root(1024);
  root["time"] = t;
  root["username"] = mqtt_user;
  root["current"] = ampsRMS;
  root["power"] = power;

  char message[100];
  serializeJson(root, message);
  
  //print to //lcd screen
   //lcd.setCursor(0, 0);
   //lcd_print(&lcd, ampsRMS, "A=");
   //lcd.setCursor(0, 1);
   //lcd_print(&lcd, power, "W=");

  // Mostramos la información por el monitor serie
  Serial.print("A = ");
  Serial.print(ampsRMS);
  Serial.print("     W = ");
  Serial.println(power);

  //publish readings
  client.publish(publish_current, message);
  delay(1000);

}

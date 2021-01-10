# Smart Electric Monitoring (currently under development)
This project aims at developing devices to measure electric power consumption from other domestic devices simultaneously, then publishing their readings to an MQTT broker, to finally visualize readings on a web page or mobile device.

## Getting started

Clone the repo on your local machine:
```
git clone https://github.com/hector6298/smart_electric_monitoring.git
cd smart_electric_monitoring
```
Then install python required dependencies:

```
sudo pip3 install -r requirements.txt
```
To recreate the device refer to CONSTRUCTION.md. Tinier, version coming!.

Open publisherSensor on your arduino IDE, then flash publisherSensor.ino on your wemos D1 R1.

Note that we make use of MQTT communication protocol to publish the power and current measurements of devices being monitored. Therefore you should create an MQTT broker with a topic named 'current'.

Please visit [iotikos](iotikos.org), or [emqx cloud](cloud.emqx.io), they offer creation of nodes free of charge.

After MQTT broker is set:
```
cd subscriberWebServer
//change macros on app.py, to fit your MQTT setup (topic, broker, user credentials)
python3 app.py
```
Go to: [http://127.0.0.1:8050/](http://127.0.0.1:8050/)
More to come!
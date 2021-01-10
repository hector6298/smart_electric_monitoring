
import random
import json
from paho.mqtt import client as mqtt_client


broker = 'o5018d87.en.emqx.cloud'
port = 11703
topic = "current"
# generate client ID with pub prefix randomly
client_id = f'hector'
username = 'hector'
password = 'hector'


def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.username_pw_set(username=username, password=password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        string = json.loads(msg.payload.decode())
        print(f"Received {string['current']} from {msg.topic} topic")

    client.subscribe(topic)
    client.on_message = on_message


def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


if __name__ == '__main__':
    run()
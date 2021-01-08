void reconnect(const char* mqttUser, const char* mqttPass, const char* resetTopic) {
  // Loop until we're reconnected

  Serial.print("Attempting MQTT connection...");
  // Create a random client ID
  String clientId = "esp8266-demo-01";

  // Attempt to connect
  if (client.connect(clientId.c_str(), mqttUser, mqttPass)) {
    Serial.println("connected");
    // Once connected, publish an announcement...
    client.publish(resetTopic, "reset");
    Serial.println("reset");
  } else {
    Serial.print("failed, rc=");
    Serial.print(client.state());
    Serial.println(" retrying in 5 seconds");
    // Wait 5 seconds before retrying
    delay(5000);
  }
}

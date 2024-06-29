import time
import json
from mqttclient import init_mqtt_client

client = init_mqtt_client()

client.subscribe("/config-response")

@client.topic_callback("/config-response")
def handle_mytopic(client, userdata, message):
  configuration = json.loads(message.payload)
  print(json.dumps(configuration, indent=2))

(rc, mid) = client.publish("/config-request", "HEHEHE")

while True:
  pass
import time
from mqttclient import init_mqtt_client

client = init_mqtt_client()

client.subscribe("/config-response")

@client.topic_callback("/config-response")
def handle_mytopic(client, userdata, message):
  print(str(message.payload, "UTF-8"))

while True:
  (rc, mid) = client.publish("/config-request", "HEHEHE")
  time.sleep(4)
  print("---------------")
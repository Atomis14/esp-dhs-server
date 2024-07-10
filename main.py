import time
import json
from mqttclient import init_mqtt_client
from configuration_type import Configuration

client = init_mqtt_client()

client.subscribe("/config-response")

@client.topic_callback("/config-response")
def handle_config_response(client, userdata, message):
  configuration: Configuration = json.loads(message.payload)
  print(json.dumps(configuration, indent=2))


rc, mid = client.publish("/config-request")

client.loop_forever() # or client.loop_start() when having own infinite loop
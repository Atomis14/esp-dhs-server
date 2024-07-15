import paho.mqtt.client as paho
import os
from dotenv import load_dotenv

load_dotenv()  # load environment variables

# called when broker responds to connection request
def _on_connect(client, userdata, flags, rc):
  if rc == 0:
    print('connection successful')
    client.subscribe('/config-response')
    client.subscribe('/device-connected')

# called when message was successfully sent to the broker
def _on_publish(client, userdata, mid):
  print('message sent, id: ' + str(mid))

# called when broker responded to subscription request
def _on_subscribe(client, userdata, mid, granted_qos):
  print('subscribed: ' + str(mid) + ' ' + str(granted_qos))

# called for each message received
def _on_message(client, userdata, msg):
  print(msg.topic + ' ' + str(msg.qos) + ' ' + str(msg.payload, 'UTF-8'))


def init_mqtt_client():
  client = paho.Client()
  client.tls_set('./ca.crt')
  client.username_pw_set(os.getenv('USERNAME'), os.getenv('PASSWORD'))
  client.on_connect = _on_connect
  client.on_publish = _on_publish
  client.on_subscribe = _on_subscribe
  client.on_message = _on_message
  client.connect(os.getenv('HOST'), 8883)
  return client

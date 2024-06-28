import paho.mqtt.client as paho
import os
from dotenv import load_dotenv, dotenv_values

load_dotenv()  # load environment variables

# called when broker responds to connection request
def on_connect(client, userdata, flags, rc):
  if rc == 0:
    print("connection successful")
    return

# called when message was successfully sent to the broker
def on_publish(client, userdata, mid):
  print("message sent, id: "+str(mid))

# called when broker responded to subscription request
def on_subscribe(client, userdata, mid, granted_qos):
  print("subscribed: "+str(mid)+" "+str(granted_qos))

# called for each message received
def on_message(client, userdata, msg):
  print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload, "UTF-8"))


def init_mqtt_client():
  client = paho.Client()
  client.tls_set("./ca.crt")
  client.username_pw_set(os.getenv("USERNAME"), os.getenv("PASSWORD"))
  client.on_connect = on_connect
  client.on_publish = on_publish
  client.on_subscribe = on_subscribe
  client.on_message = on_message
  client.connect(os.getenv("HOST"), 8883)
  client.loop_start()
  return client

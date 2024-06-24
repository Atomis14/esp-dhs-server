import paho.mqtt.client as paho
import time
import os
from dotenv import load_dotenv, dotenv_values

load_dotenv() # load environment variables

# called when broker responds to connection request
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("connection successful")
        return
    print("Connection unsuccessful, code: ", rc)

# called when message was successfully sent to the broker
def on_publish(client, userdata, mid):
    #print("mid: "+str(mid))
    pass

# called when broker responded to subscription request
def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed: "+str(mid)+" "+str(granted_qos))

# called for each message received
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload, "UTF-8"))

client = paho.Client()
client.username_pw_set(os.getenv("USERNAME"), os.getenv("PASSWORD"))
client.on_connect = on_connect
client.on_publish = on_publish
client.on_subscribe = on_subscribe
client.on_message = on_message
client.connect("localhost", 1883)
client.subscribe("/encyclopedia/#")

client.loop_start()

while True:
    temperature = "HELLO"
    (rc, mid) = client.publish("/encyclopedia/test", str(temperature), qos=1)
    time.sleep(2)
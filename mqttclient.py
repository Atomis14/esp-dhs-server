import paho.mqtt.client as paho
import time


# called when broker responds to connection request
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("connection successful")
        return
    print("Connection unsuccessful, code: ", rc)

# called when message was successfully sent to the broker
def on_publish(client, userdata, mid):
    print("mid: "+str(mid))

# called when broker responded to subscription request
def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed: "+str(mid)+" "+str(granted_qos))

# called for each message received
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload, 'UTF-8'))

client = paho.Client()
client.on_connect = on_connect
client.on_publish = on_publish
client.on_subscribe = on_subscribe
client.on_message = on_message
client.connect('broker.mqttdashboard.com', 1883)
client.subscribe('encyclopedia/#')

client.loop_start()

while True:
    temperature = "HELLO"
    (rc, mid) = client.publish('/encyclopedia/test', str(temperature), qos=1)
    time.sleep(5)
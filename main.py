import json
import time
import database
from datetime import datetime, timezone
from mqtt_client import init_mqtt_client, publish_message
from user_types.configuration_type import Configuration
from user_types.security_features_type import SecurityFeatures
from compile import compile_secure
from models import Message, Configuration, Flash

run_main_loop = True
client = init_mqtt_client()

@client.topic_callback('/config-response')
def handle_config_response(client, userdata, message):
  global run_main_loop
  print('/config-response Message Received')
  configuration: Configuration = json.loads(message.payload)
  #print(json.dumps(configuration, indent=2))
  message_db = Message(topic=message.topic, type='received')
  configuration_db = Configuration(message=message_db, configuration=str(configuration))
  database.add_row([message_db, configuration_db])
  features: SecurityFeatures = [] # security features that should be activated
  if configuration['flash_encryption_enabled'] == False:
    features.append('flashencryption')
  if configuration['secure_boot_enabled'] == False:
    features.append('secureboot')
  if configuration['memory_protection_enabled'] == False:
    features.append('memoryprotection')
  if features: # features array not empty
    print('The following features will be activated:', features)
    run_main_loop = False
    flash_db = Flash(features=str(features), status='pending')
    database.add_row(flash_db)  # already add here to DB in case compile_secure fails
    try:
      compile_secure(features)
      flash_db.status = 'success'
    except Exception as e:
      print("Could not flash firmware:", e)
      flash_db.status = 'error'
    flash_db.end = datetime.now(timezone.utc).replace(microsecond=0)
    database.add_row(flash_db)
    run_main_loop = True

@client.topic_callback('/device-connected')
def handle_device_start(client, userdata, message):
  print('/device-connected Message Received')
  configuration: Configuration = json.loads(message.payload)
  #print(json.dumps(configuration, indent=2))
  message_db = Message(topic=message.topic, type='received')
  configuration_db = Configuration(message=message_db, configuration=str(configuration))
  database.add_row([message_db, configuration_db])

client.loop_start()
while True:
  if run_main_loop:
    publish_message(client, '/config-request')
    time.sleep(10)  # request every minute

""" publish_message(client, '/config')
client.loop_forever() # or client.loop_start() when having own infinite loop """
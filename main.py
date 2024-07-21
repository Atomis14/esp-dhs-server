import json
import time
from datetime import datetime, timezone
import database
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
  print('Config Response Message Received')
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
    flash_db = Flash(features=str(features))
    database.add_row(flash_db)  # already add here to DB in case compile_secure fails
    compile_secure(features)
    flash_db.end = datetime.now(timezone.utc).replace(microsecond=0)
    database.add_row(flash_db)
    run_main_loop = True

@client.topic_callback('/device-connected')
def handle_device_start(client, userdata, message):
  print('"Back Online" Message Received')
  #configuration: Configuration = json.loads(message.payload)
  #print(json.dumps(configuration, indent=2))
  database.add_row(Message(topic=message.topic, type='received'))

client.loop_start()
while True:
  if run_main_loop:
    publish_message(client, '/config-request')
    time.sleep(5)

""" publish_message(client, '/config-request')
client.loop_forever() # or client.loop_start() when having own infinite loop """
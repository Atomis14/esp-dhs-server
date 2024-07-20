import json
import time
import database
from mqtt_client import init_mqtt_client, publish_message
from user_types.configuration_type import Configuration
from user_types.security_features_type import SecurityFeatures
from compile import compile_secure
from models import Message, Configuration


client = init_mqtt_client()

@client.topic_callback('/config-response')
def handle_config_response(client, userdata, message):
  print('Config Response Message Received')
  configuration: Configuration = json.loads(message.payload)
  print(json.dumps(configuration, indent=2))
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
    compile_secure(features)

@client.topic_callback('/device-connected')
def handle_device_start(client, userdata, message):
  print('"Back Online" Message Received')
  configuration: Configuration = json.loads(message.payload)
  print(json.dumps(configuration, indent=2))
  database.add_row(Message(topic=message.topic, type='received'))

publish_message(client, '/config-request')


client.loop_forever() # or client.loop_start() when having own infinite loop
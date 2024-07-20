import json
import time
from mqtt_client import init_mqtt_client, publish_message
from user_types.configuration_type import Configuration
from user_types.security_features_type import SecurityFeatures
from compile import compile_secure
import database
from models import Message


client = init_mqtt_client()

@client.topic_callback('/config-response')
def handle_config_response(client, userdata, message):
  print('Config Response Message Received')
  configuration: Configuration = json.loads(message.payload)
  print(json.dumps(configuration, indent=2))
  features: SecurityFeatures = [] # security features that should be activated
  if configuration['flash_encryption_enabled'] == False:
    features.append('flashencryption')
  if configuration['secure_boot_enabled'] == False:
    features.append('secureboot')
  if configuration['memory_protection_enabled'] == False:
    features.append('memoryprotection')
  if configuration: # configuration array not empty
    print('The following features will be activated:', features)
    compile_secure(features)

@client.topic_callback('/device-connected')
def handle_device_start(client, userdata, message):
  print('Device Connected Message Received')
  configuration: Configuration = json.loads(message.payload)
  print(json.dumps(configuration, indent=2))


publish_message(client, '/config-request')


client.loop_forever() # or client.loop_start() when having own infinite loop
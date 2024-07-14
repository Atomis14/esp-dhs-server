import json
from mqtt_client import init_mqtt_client
from user_types.configuration_type import Configuration
from user_types.security_features_type import SecurityFeatures
from compile import compile_secure

client = init_mqtt_client()

client.subscribe('/config-response')

@client.topic_callback('/config-response')
def handle_config_response(client, userdata, message):
  configuration: Configuration = json.loads(message.payload)
  print(json.dumps(configuration, indent=2))
  features: SecurityFeatures = [] # security features that should be activated
  if configuration['flash_encryption_enabled'] == False:
    features.append('flashencryption')
  if configuration['secure_boot_enabled'] == False:
    features.append('secureboot')
  print('The following features will be activated:', features)
  if configuration != []:
    compile_secure(features)

rc, mid = client.publish('/config-request')

client.loop_forever() # or client.loop_start() when having own infinite loop
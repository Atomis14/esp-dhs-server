import os
import json
import time
import database
from dotenv import load_dotenv
from datetime import datetime, timezone
from mqtt_client import init_mqtt_client, publish_message
from compile import compile_secure
from models import Message, Configuration, Flash

load_dotenv()

run_main_loop = True
client = init_mqtt_client()
current_config = {} # stores the last known configuration of the ESP32-S3

def compare_configurations(new_config):
  global current_config
  if current_config != {}:
    change_detected = False
    output = ""
    for key in current_config:
      if current_config[key] != new_config[key]:
        change_detected = True
        output += key + ': ' + str(current_config[key]) + ' → ' + str(new_config[key]) + '\n'
    if change_detected:
      print('\nChange in config detected:')
      print(output)
  current_config = new_config

@client.topic_callback('/config-response')
def handle_config_response(client, userdata, message):
  global run_main_loop
  print('/config-response message received')
  configuration = json.loads(message.payload)
  compare_configurations(configuration)
  #print(json.dumps(configuration, indent=2))
  message_db = Message(topic=message.topic, type='received', created_at=datetime.now(timezone.utc))
  configuration_db = Configuration(message=message_db, **configuration)
  database.add_row([message_db, configuration_db])
  features = [] # security features that should be activated
  if configuration['flash_encryption_enabled'] == False:
    features.append('flashencryption')
  if configuration['secure_boot_enabled'] == False:
    features.append('secureboot')
  if configuration['memory_protection_enabled'] == False:
    features.append('memoryprotection')
  if features: # features array not empty
    print('The following features will be activated:', features)
    run_main_loop = False
    flash_db = Flash(status='pending',
                     start=datetime.now(timezone.utc),
                     flashencryption='flashencryption' in features,
                     secureboot='secureboot' in features,
                     memoryprotection='memoryprotection' in features)
    database.add_row(flash_db)  # already add here to DB in case compile_secure fails
    try:
      compile_secure(features)
      flash_db.status = 'success'
    except Exception as e:
      print('Could not flash firmware:', e, '\nYou may need to restart the device manually.')
      flash_db.status = 'error'
    flash_db.end = datetime.now(timezone.utc)
    database.add_row(flash_db)
    run_main_loop = True

@client.topic_callback('/device-connected')
def handle_device_start(client, userdata, message):
  print('/device-connected message received')
  configuration = json.loads(message.payload)
  compare_configurations(configuration)
  #print(json.dumps(configuration, indent=2))
  message_db = Message(topic=message.topic, type='received', created_at=datetime.now(timezone.utc))
  configuration_db = Configuration(message=message_db, **configuration)
  database.add_row([message_db, configuration_db])

client.loop_start()
while True:
  if run_main_loop:
    publish_message(client, '/config-request')
    time.sleep(int(os.getenv('REQUEST_INTERVAL')))


""" publish_message(client, '/config')
client.loop_forever() # or client.loop_start() when having own infinite loop """
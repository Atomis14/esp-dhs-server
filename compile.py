import subprocess
import time
import esptool
import kconfiglib
import os
import shutil
import datetime
from dotenv import load_dotenv
from typing import Literal
from user_types.security_features_type import SecurityFeatures
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

load_dotenv()

# constants from .env file
ESP_IDF_EXPORT_SCRIPT_PATH  = os.getenv('ESP_IDF_EXPORT_SCRIPT_PATH')
PROJECT_PATH                = os.getenv('PROJECT_PATH')
ESP_IDF_PATH                = os.getenv('ESP_IDF_PATH')
BACKUP_DIR_PATH             = os.getenv('BACKUP_DIR_PATH')
KEY_FILE_NAME               = os.getenv('KEY_FILE_NAME')
PORT                        = os.getenv('PORT')
TARGET                      = os.getenv('TARGET')
BAUD_RATE                   = os.getenv('BAUD_RATE')

# set up the esp idf environment in the process
init_commands = (
  './run_with_env.sh', ESP_IDF_EXPORT_SCRIPT_PATH,  # initialize the esp-idf environment
  'idf.py', # call esp idf
  '--project-dir', PROJECT_PATH, '--port', PORT,  # define directory of the project and port for flashing
)


def _run_commands(commands):
  """Run commands and print output and errors to the console."""
  process = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
  while True: # print output in realtime
    output = process.stdout.readline()
    if output == "" and process.poll() is not None:
      break
    if output:
      print(output.strip())
  for line in process.stdout: # any remaining output
    print(line.strip())


def _delete_sdkconfig():
  """Delete the sdkconfig file in the project directory."""
  sdkconfig_path = PROJECT_PATH + '/sdkconfig'
  if os.path.exists(sdkconfig_path):
    os.remove(PROJECT_PATH + '/sdkconfig')
  else:
    print(f'sdkconfig at path {sdkconfig_path} does not exist.')


def _flash_bootloader():
  """Flashes only the bootloader to the ESP."""
  command = (
    '--chip', TARGET,
    f'--port={PORT}',
    f'--baud={BAUD_RATE}',
    '--before=default_reset',
    '--after=no_reset',
    '--no-stub',
    'write_flash',
    '--flash_mode', 'dio',
    '--flash_freq', '80m',
    '--flash_size', 'keep', '0x0',
    PROJECT_PATH + '/build/bootloader/bootloader.bin'
  )
  esptool.main(command)


def _generate_signing_key():
  """Generate the secure boot signing key and copy it in a pem file to the project path."""
  key_file_path = PROJECT_PATH + '/' + KEY_FILE_NAME
  # backup old key if exists
  if os.path.exists(key_file_path):
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    backup_key_name = 'backup_' + current_datetime + '_' + KEY_FILE_NAME
    shutil.copyfile(key_file_path, BACKUP_DIR_PATH + '/' + backup_key_name)
  # create new key
  private_key = rsa.generate_private_key(public_exponent=65537, key_size=3072)
  private_key_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.TraditionalOpenSSL,
    encryption_algorithm=serialization.NoEncryption()
  )
  with open(key_file_path, 'w') as key_file:
    key_file.write(private_key_pem.decode())


def _erase_flash():
  """Erase the ESP flash memory completely. Erasing the flash doesn't work with idf.py due to a bug, therefore done via esptool."""
  command = (
    '--chip', TARGET,
    f'--port={PORT}',
    'erase_flash')
  esptool.main(command)


def _set_debug_sdkconfig(kconfig):
  """Adjust values in the sdkconfig file that are necessary for debugging, especially for using virtual efuses."""
  kconfig.syms['PARTITION_TABLE_CUSTOM']      .set_value('y')       # contains efuse partition to keep values after reboot
  kconfig.syms['PARTITION_TABLE_OFFSET']      .set_value('0x10000') # secure boot and flash encryption make bootloader bigger -> bigger offset needed
  kconfig.syms['EFUSE_VIRTUAL']               .set_value('y')       # do not destroy efuses permanently while debugging
  kconfig.syms['EFUSE_VIRTUAL_KEEP_IN_FLASH'] .set_value('y')       # necessary for debugging flash encryption and secure boot with virtual efuses


def _change_security_features(mode: Literal['activate', 'deactivate'], features: SecurityFeatures = None):
  """
  Activate or deactivate the security features of the ESP.
  In activation mode, the security features listed in the first parameter are activated.
  In deactivation mode, all security features are turned off in the sdkconfig, the features parameter does not matter.
  """
  if mode == 'activate' and features == None:
    raise Exception('Cannot activate features if none are listed.') # this line is reachable, even if the IDE tells it's not

  kconfig_path = ESP_IDF_PATH + '/Kconfig'      # base kconfig file from which all other kconfigs are loaded
  sdkconfig_path = PROJECT_PATH + '/sdkconfig'  # file holding the actual values of the kconfig variables

  if not os.path.exists(sdkconfig_path):
    print('Create the sdkconfig file at', sdkconfig_path)
    open(sdkconfig_path, 'w')
  
  # necessary environment variables for loading the whole kconfig
  os.environ['COMPONENT_KCONFIGS_PROJBUILD_SOURCE_FILE'] = PROJECT_PATH + '/build/kconfigs_projbuild.in'  # file with the paths to all Kconfig.projbuild files of project components (project-specific)
  os.environ['COMPONENT_KCONFIGS_SOURCE_FILE'] = PROJECT_PATH + '/build/kconfigs.in'  # file with the paths of all Kconfig files of different esp idf components (not specific to the project)
  os.environ['IDF_PATH'] = ESP_IDF_PATH
  os.environ['IDF_TARGET'] = TARGET
  
  kconfig = kconfiglib.Kconfig(kconfig_path)
  kconfig.load_config(sdkconfig_path)
  
  _set_debug_sdkconfig(kconfig)

  if mode == 'activate':
    if 'secureboot' in features:
      kconfig.syms['SECURE_BOOT'].set_value('y')
    if 'flashencryption' in features:
      kconfig.syms['SECURE_FLASH_ENC_ENABLED'].set_value('y')
    if 'memoryprotection' in features:
      kconfig.syms['ESP_SYSTEM_MEMPROT_FEATURE'].set_value('y')
  elif mode == 'deactivate':
    kconfig.syms['SECURE_BOOT']               .set_value('n')
    kconfig.syms['SECURE_FLASH_ENC_ENABLED']  .set_value('n')
    kconfig.syms['ESP_SYSTEM_MEMPROT_FEATURE'].set_value('n')
  else:
    raise TypeError('Invalid value for the mode variable.')
  
  kconfig.write_config(sdkconfig_path)    


def _run_application():
  """
  Run the application that resides in ESP32 flash.
  This is needed to restart the ESP32 after secure boot and flash encryption are activated, since it is not done automatically after flashing.
  """
  command = (
    #'--chip', TARGET,
    f'--port={PORT}',
    'run')
  esptool.main(command)


def compile_standard():
  """Compile and flash the project without security features."""
  os.environ['IDF_TARGET'] = TARGET
  _change_security_features('deactivate')
  _erase_flash()  # just to be sure
  commands = init_commands + (
    'fullclean',  # delete the build directory
    'build',      # build the binary for the specified target
    'flash'       # flash the binary to the specified port
  )
  _run_commands(commands)
  print("Finished standard compiling and flashing.")


def compile_secure(features: SecurityFeatures = None):
  """
  Compile and flash project with activated secure boot and flash encryption.
  Features are activated additively, e.g. if secure boot was already activated and the function gets called only
  with the flash encryption parameter, flash encryption and secure boot will both be activated in the end.
  """
  os.environ['IDF_TARGET'] = TARGET
  _generate_signing_key()
  _erase_flash()
  _change_security_features('activate', features)
  time.sleep(1)   # necessary so that the right files are flashed
  commands = init_commands + (
    'fullclean',  # delete the build directory
    'bootloader', # compile the bootloader
  )
  _run_commands(commands)
  time.sleep(1)
  _flash_bootloader()
  time.sleep(1)
  commands = init_commands + (
    'flash', # build and flash the partition table and app image
  )
  _run_commands(commands)
  _run_application()  # manually restart the ESP32
  print("Finished secure compiling and flashing.")

#compile_secure(['flashencryption', 'memoryprotection', 'secureboot'])
#compile_standard()
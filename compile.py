import subprocess
import time
import esptool
import kconfiglib
import os
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

ESP_IDF_EXPORT_SCRIPT_PATH = "/Users/michelsabbatini/esp/v5.2.1/esp-idf/export.sh"
PROJECT_PATH = "/Users/michelsabbatini/esp/v5.2.1/projects/security-test-2"
ESP_IDF_PATH = "/Users/michelsabbatini/esp/v5.2.1/esp-idf"
KEY_FILE_NAME = "secure_boot_signing_key.pem"
PORT = "/dev/cu.usbserial-140"
TARGET = "esp32s3"
BAUD_RATE = 115200

# set up the esp idf environment in the process
init_commands = (
  "./run_with_env.sh", ESP_IDF_EXPORT_SCRIPT_PATH,  # initialize the esp-idf environment
  "idf.py", # call esp idf
  "--project-dir", PROJECT_PATH, "--port", PORT,  # define directory of the project and port for flashing
)


def _run_commands(commands):
  """Run commands and print output and errors to the console."""
  process = subprocess.run(commands, capture_output=True)
  print(process.stdout.decode("utf-8"))
  print(process.stderr.decode("utf-8"))

def _delete_sdkconfig():
  sdkconfig_path = PROJECT_PATH + "/sdkconfig"
  if os.path.exists(sdkconfig_path):
    os.remove(PROJECT_PATH + "/sdkconfig")
  else:
    print(f"sdkconfig at path {sdkconfig_path} does not exist.")

def compile_standard():
  """Compile and flash the project without security features."""
  os.environ["IDF_TARGET"] = TARGET
  _delete_sdkconfig()  # to get rid of activated security features
  _erase_flash() # just to be sure
  commands = init_commands + (
    "fullclean",  # delete the build directory
    "build",      # build the binary for the specified target
    "flash"       # flash the binary to the specified port
  )
  _run_commands(commands)


def _flash_bootloader():
  """Flashes only the bootloader to the esp."""
  command = (
    "--chip", TARGET,
    f"--port={PORT}",
    f"--baud={BAUD_RATE}",
    "--before=default_reset",
    "--after=no_reset",
    "--no-stub",
    "write_flash",
    "--flash_mode", "dio",
    "--flash_freq", "80m",
    "--flash_size", "keep", "0x0",
    PROJECT_PATH + "/build/bootloader/bootloader.bin"
  )
  esptool.main(command)


def _generate_signing_key():
  """Generate the secure boot signing key and copy it in a pem file to the project path."""
  private_key = rsa.generate_private_key(public_exponent=65537, key_size=3072)
  private_key_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.TraditionalOpenSSL,
    encryption_algorithm=serialization.NoEncryption()
  )
  key_file_path = PROJECT_PATH + "/" + KEY_FILE_NAME
  with open(key_file_path, "w") as key_file:
    key_file.write(private_key_pem.decode())


def _erase_flash():
  """Erase the esp flash memory completely."""
  command = (
    "--chip", TARGET,
    f"--port={PORT}",
    "erase_flash")
  esptool.main(command)


def _adjust_sdkconfig():
  kconfig_path = ESP_IDF_PATH + "/Kconfig"      # base kconfig file from which all other kconfigs are loaded
  sdkconfig_path = PROJECT_PATH + "/sdkconfig"  # file holding the actual values of the kconfig variables

  if not os.path.exists(sdkconfig_path):
    print("Create the sdkconfig file at", sdkconfig_path)
    open(sdkconfig_path, "w")
  
  # necessary environment variables for loading the whole kconfig
  os.environ["COMPONENT_KCONFIGS_PROJBUILD_SOURCE_FILE"] = PROJECT_PATH + "/build/kconfigs_projbuild.in"  # file with the paths to all Kconfig.projbuild files of project components (project-specific)
  os.environ["COMPONENT_KCONFIGS_SOURCE_FILE"] = PROJECT_PATH + "/build/kconfigs.in"  # file with the paths of all Kconfig files of different esp idf components (not specific to the project)
  os.environ["IDF_PATH"] = ESP_IDF_PATH
  os.environ["IDF_TARGET"] = TARGET
  
  kconfig = kconfiglib.Kconfig(kconfig_path)
  kconfig.load_config(sdkconfig_path)
  
  kconfig.syms["SECURE_BOOT"]                 .set_value("y")
  kconfig.syms["SECURE_FLASH_ENC_ENABLED"]    .set_value("y")
  kconfig.syms["PARTITION_TABLE_CUSTOM"]      .set_value("y")
  kconfig.syms["PARTITION_TABLE_OFFSET"]      .set_value("0x10000")
  kconfig.syms["EFUSE_VIRTUAL"]               .set_value("y")
  kconfig.syms["EFUSE_VIRTUAL_KEEP_IN_FLASH"] .set_value("y")
  
  kconfig.write_config(sdkconfig_path)    


def compile_secure():
  """Compile and flash project with activated secure boot and flash encryption."""
  os.environ["IDF_TARGET"] = TARGET
  _generate_signing_key()
  _erase_flash()
  _adjust_sdkconfig()
  time.sleep(1)   # necessary so that the right files are flashed
  commands = init_commands + (
    "fullclean",  # delete the build directory
    "bootloader", # compile the bootloader
  )
  _run_commands(commands)
  time.sleep(1)
  _flash_bootloader()
  time.sleep(1)
  commands = init_commands + (
    "flash", # build and flash the partition table and app image
  )
  _run_commands(commands)

#compile_standard()
#compile_secure()
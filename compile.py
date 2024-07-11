import subprocess
import time
import esptool
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

TARGET="esp32s3"
ESP_IDF_EXPORT_SCRIPT_PATH = "/Users/michelsabbatini/esp/v5.2.1/esp-idf/export.sh"
PROJECT_PATH="/Users/michelsabbatini/esp/v5.2.1/projects/security-test-2"
PORT="/dev/cu.usbserial-140"
BAUD_RATE=115200
KEY_FILE_NAME="secure_boot_signing_key.pem"

# needed for initialization of erase-flash (does not work when target is set)
init_commands = (
  # initialize the esp-idf environment
  "./run_with_env.sh", ESP_IDF_EXPORT_SCRIPT_PATH,
  # call esp idf
  "idf.py",
  # define directory of the project and port for flashing
  "--project-dir", PROJECT_PATH, "--port", PORT,
  # set the target architecture (e.g. esp32 or esp32s3)
  "set-target", TARGET
)

def run_and_print(command):
  """Run commands and print output and errors to the console."""
  process = subprocess.run(command, capture_output=True)
  print(process.stdout.decode("utf-8"))
  print(process.stderr.decode("utf-8"))

def compile_standard():
  """Compile and flash the project without secure boot or flash encryption."""
  erase_flash() # just to be sure
  commands = init_commands + (
    # build the binary for the specified target
    "build",
    # flash the binary to the specified port
    "flash"
  )
  start = time.time()
  run_and_print(commands)
  print("elapsed time compile_and_flash: ", time.time()-start)

def flash_bootloader():
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
    "/Users/michelsabbatini/esp/v5.2.1/projects/security-test-2/build/bootloader/bootloader.bin"
  )
  esptool.main(command)

def erase_flash():
  """Erase the esp flash memory completely."""
  command = (
    "--chip", TARGET,
    f"--port={PORT}",
    "erase_flash")
  esptool.main(command)

def generate_signing_key():
  private_key = rsa.generate_private_key(public_exponent=65537, key_size=3072)
  private_key_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.TraditionalOpenSSL,
    encryption_algorithm=serialization.NoEncryption()
  )
  key_file_path = PROJECT_PATH + "/" + KEY_FILE_NAME
  with open(key_file_path, "w") as key_file:
    key_file.write(private_key_pem.decode())


def compile_secure():
  """Compile and flash project with activated secure boot and flash encryption."""
  # TODO: check if sdkconfig.defaults exists
  generate_signing_key()
  erase_flash()
  commands = init_commands + (
    # delete the build directory
    "fullclean",
    # compile the bootloader
    "bootloader",
  )
  run_and_print(commands)
  time.sleep(1)
  flash_bootloader()
  commands = init_commands + (
    # build and flash the partition table and app image
    "flash",
  )
  time.sleep(1)
  run_and_print(commands)

#compile_standard()
compile_secure()
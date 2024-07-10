import subprocess
import time
import esptool

target="esp32s3"
esp_idf_export_script_path = "/Users/michelsabbatini/esp/v5.2.1/esp-idf/export.sh"
project_path="/Users/michelsabbatini/esp/v5.2.1/projects/security-test-2"
port="/dev/cu.usbserial-140"

def run_and_print(command):
  """Run commands and print them to the console."""
  process = subprocess.run(command, capture_output=True)
  print(process.stdout.decode("utf-8"))
  print(process.stderr.decode("utf-8"))

def compile_and_flash():
  """Compile and flash the project raw without secure boot or flash encryption."""
  commands = (
    # set the target ESP architecture
    ["idf.py", "--project-dir", project_path, "set-target", target],
    # build the binary
    ["idf.py", "--project-dir", project_path, "build"],
    # flash the binary to the ESP
    ["idf.py", "--project-dir", project_path, "--port", port, "flash"]
  )

  start = time.time()
  for command in commands:
    idf_init_command = ["./run_with_env.sh", esp_idf_export_script_path]  # initialize the esp-idf environment
    command = idf_init_command + command
    run_and_print(command)
  print(time.time()-start)

compile_and_flash()
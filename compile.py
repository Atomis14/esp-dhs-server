import subprocess
import esptool

def compile_project_subprocess():
  esp_idf_export_script_path = "/Users/michelsabbatini/esp/v5.2.1/esp-idf/export.sh"
  project_path=""
  commands = [
    "./run_with_env.sh", esp_idf_export_script_path,
  ]
  a = subprocess.run(commands, capture_output=True)
  print(a.stdout.decode("utf-8"))

def compile_project_esptool():
  esptool.main([])
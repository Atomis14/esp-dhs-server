import subprocess

esp_idf_export_script_path = "/Users/michelsabbatini/esp/v5.2.1/esp-idf/export.sh"

a = subprocess.run(["./run_with_env.sh", esp_idf_export_script_path], capture_output=True)

print(a.stdout.decode("utf-8"))
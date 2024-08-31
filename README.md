# ESP-DHS Server

**ESP**32-S3 **D**evice **H**ardening **S**ystem Server

Application running on a host machine that extracts the security configuration of an ESP32-S3 and flashes new firmware to the microcontroller if necessary.

This README includes instructions for both the python server contained in this repository and the MQTT broker.

## Python Server

To run the server, a Python installation version 3.9.6 or higher is necessary. The server needs access to the directory containing the source code of the ESP32-S3 firmware.

1. Install the necessary Python packages on your machine:
    - `esptool` for flashing firmware onto the ESP32 over USB
    - `paho-mqtt` for the MQTT connection over TCP
    - `dotenv` to read environment variables from the `.env` file
    - `kconfiglib` to programmatically edit the sdkconfig files
    - `SQLAlchemy` for the communication with the SQLite database
2. Copy the `.env.example` file, rename it to `.env` and adjust the environment variables as needed.
3. To start the server, run the `main.py` file.

## Mosquitto Setup

Mosquitto is the software used to run the MQTT broker. These installation guidelines assume the broker runs on the same machine as the server.

### Install Mosquitto


1. mosquitto by running: `brew install mosquitto` 
2. Configure the broker
    - Create a password file by running: `mosquitto_passwd -c <path to password file> <username>`
    - Add the `listener` option to the `mosquitto.conf` file  (located at `/opt/homebrew/Cellar/mosquitto/2.0.18/etc/mosquitto}`) in order to not only allow connections from the same machine: `listener 1883`
    - Add the `password_file` option to `mosquitto.conf`: `password_file <path to the password file>`}
    - Grant permission to the user to read/write the password file by running: `chmod 0700 <path to password file>`
3. Start the broker by running: `/opt/homebrew/opt/mosquitto/sbin/mosquitto -c /opt/homebrew/etc/mosquitto/mosquitto.conf`

### Setup TLS Encryption

1. Create a key pair for the Certificate Authority (CA) by running: `openssl genrsa -out ca.key 2048`
2. Create certificate for CA using private key from step 1 by running: `openssl req -new -x509 -days 1826 -key ca.key -out ca.crt`
3. Fill in the requested information, remember the fully qualified domain name (FQDN), which could be e.g. the IP address of the broker. The FQDN can be retrieved by running `hostname -f`.
4. Create server key pair that is used by the broker by running: `openssl genrsa -out server.key`
5. Create certificate request using the server key from before (use FQDN from before as the common name) by running: `openssl req -new -out server.csr -key server.key`
6. Use CA key to verify and sign the server certificate, this creates the server.crt file: `openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 360`
7. Copy the following files to a folder under the mosquitto folder: `ca.crt`, `server.crt`, `server.key`
8. Copy `ca.crt` to the root directory of the ESP-DHS server and `/components/dhs_mqtt` directory of the ESP32-S3 firmware project
9. Edit the `mosquitto.conf` file:
    - Change `listener 1883` to `listener 8883`
    - Add `cafile <path to ca.crt>`
    - Add `keyfile <path to server.key>`
    - Add `certfile <path to server.crt>`
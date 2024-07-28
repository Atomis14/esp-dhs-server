# ESP-DHS Server

**ESP**32-S3 **D**evice **H**ardening **S**ystem

This README includes instructions for the python server contained in this repository but also the MQTT broker.

## Python Server

Python version: 3.9.6

### Setup

1. Install the necessary packages:
- `esptool` (flash firmware to the ESP over USB)
- `paho` (MQTT connection over TCP)
- `dotenv` (read data from .env file)
- `kconfiglib` (programmatically edit sdkconfig files)
- `SQLAlchemy` (communication with SQLite database)

2. Create the `.env` file in the root directory (copy the .env.example file and adjust the values)

3. Copy the SSL certificate for the connection with the MQTT broker to the root directory (make sure it is called `ca.crt`)

## MQTT Broker

Procedure on macOS 14.5 (Sonoma) with Homebrew, may vary for different operating systems

### Setup

- install mosquitto: `brew install mosquitto`
- configure the broker
  - create password file: `mosquitto_passwd -c <path to password file> <username>`
  - enter desired password twice
  - add listener option to mosquitto.conf in order to not only allow connections from same machine (located at /opt/homebrew/Cellar/mosquitto/2.0.18/etc/mosquitto):  
  `listener 1883`
  - add password_file option to mosquitto.conf:  
  `password_file <path to the password file>`
  - grant permission to the user to read/write the password file: `chmod 0700 <path to password file>`
- run mosquitto: `/opt/homebrew/opt/mosquitto/sbin/mosquitto -c /opt/homebrew/etc/mosquitto/mosquitto.conf`

### Secure Broker with TLS

1. create a key pair for the Certificate Authority (CA)  
`openssl genrsa -out ca.key 2048`
2. create certificate for CA using private key from step 1  
`openssl req -new -x509 -days 1826 -key ca.key -out ca.crt`  
fill in the requested information, remember the fully qualified domain name (FQDN), which could be e.g. the IP address of the broker (use here "localhost")
3. create server key pair that is used by the broker  
`openssl genrsa -out server.key`
4. create certificate request using the server key from before (use FQDN from before as the common name)  
`openssl req -new -out server.csr -key server.key`
5. use CA key to verify and sign the server certificate -> this creates the server.crt file  
`openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 360`
6. copy the following files to a folder under the mosquitto folder: `ca.crt`, `server.crt`, `server.key`  
(the mosquitto folder is under `/opt/homebrew/Cellar/mosquitto/2.0.18/etc/mosquitto`)
7. copy `ca.crt` to the server (i.e. this python application) and the client (i.e. the ESP32)
8. edit mosquitto.conf file  
  • change `listener 1883` to `listener 8883`  
  • add `cafile <path to ca.crt)`  
  • add `keyfile <path to server.key>`  
  • add `certfile <path to server.crt>`
9. client configuration (for python server)  
  • add the following line `client.tls_set(<path to ca.crt>)`
  • change the listening port to 8883
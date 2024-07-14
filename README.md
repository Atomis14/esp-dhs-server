# BA-project Server

## Python Application

- install esptool: `pip install esptool`  
used to flash firmware to the ESP over USB
- (import pyserial: `pip install pyserial`)  
used for serial communication over USB
- install paho `pip install paho-mqtt`  
used for MQTT connection over TCP
- install dotenv `pip install python-dotenv`  
used to read data from .env file

### Environment Variables

Create a .env file in the root directory, .env.example provides the structure and example values which should be adjusted.

## MQTT Broker

Procedure used on macOS 14.5 (Sonoma)

### Installation

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



### Debugging

For debugging (without TLS), the broker with URL `mqtt://broker.mqttdashboard.com` can be used.
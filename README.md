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

Create a .env file in the root directory with the following content:
```
USERNAME=<username for mqtt broker>
PASSWORD=<password for mqtt broker>
```

## MQTT Broker

Procedure used on macOS 14.5 (Sonoma)

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
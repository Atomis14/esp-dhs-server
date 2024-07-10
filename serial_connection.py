""" import serial
import time

port = serial.Serial("/dev/cu.usbserial-1130", 115200, timeout=1)

# read one character as default
def read_serial(nr_chars=1024):
  data = port.read(nr_chars)
  return data.decode()

def write_serial():
  #for i in range(1,100):
  while(True):
    port.write(b"0123456789012345678\n")

write_serial() """


""" import serial
import time

def main():
    ser = serial.Serial("/dev/cu.usbserial-1130", 115200, timeout=1)

    while True:
        # Data to send
        data_to_send = "Hello from Python!\n"
        
        # Write data to the UART
        ser.write(data_to_send.encode('ascii'))
        print(f"Sent: {data_to_send.strip()}")
        
        # Wait for a response
        time.sleep(0.5)
        
        # Read echoed data from the UART
        if ser.in_waiting > 0:
            received_data = ser.read(ser.in_waiting).decode('ascii')
            print(f"Received: {received_data.strip()}")

        # Sleep for a while before sending the next message
        time.sleep(1)

if __name__ == "__main__":
    main() """
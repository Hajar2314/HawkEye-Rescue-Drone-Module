import serial
import pynmea2

port = "/dev/serial0"
baudrate = 9600

ser = serial.Serial(port, baudrate, timeout=1)

print("Waiting for GPS fix...")

while True:
    line = ser.readline().decode('ascii', errors='replace')
    
    if line.startswith('$GPGGA'):
        try:
            msg = pynmea2.parse(line)
            
            if msg.latitude and msg.longitude:
                print(f"Latitude: {msg.latitude} {msg.lat_dir}")
                print(f"Longitude: {msg.longitude} {msg.lon_dir}")
                print("-" * 40)
        except pynmea2.ParseError:
            continue

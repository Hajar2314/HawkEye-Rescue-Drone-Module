import serial
import pynmea2

port = "/dev/serial0"
baudrate = 9600

ser = serial.Serial(port, baudrate, timeout=1)

print("Waiting for GPS fix...")

while True:
    try:
        line = ser.readline().decode('ascii', errors='replace').strip()
    except UnicodeDecodeError:
        continue  # Skip invalid lines

    if line.startswith('$GPGGA'):
        try:
            msg = pynmea2.parse(line)

            # Check if GPS has a valid fix (msg.gps_qual > 0)
            if msg.gps_qual and int(msg.gps_qual) > 0:
                print(f"Latitude: {msg.latitude} {msg.lat_dir}")
                print(f"Longitude: {msg.longitude} {msg.lon_dir}")
            else:
                print("No GPS fix yet...")

            print("-" * 40)

        except pynmea2.ParseError:
            continue

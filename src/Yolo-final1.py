import cv2
import os
import time
from picamera2 import Picamera2
from ultralytics import YOLO
import requests
from datetime import datetime

# Load YOLOv8 Nano model
model = YOLO("yolov8n.pt")

# Initialize Pi Camera
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": "BGR888"}))
picam2.start()

# Ensure the Screenshot-dump directory exists
os.makedirs("Screenshot-dump", exist_ok=True)

# Find the location of the Pi using IP address-based geolocation
def get_location_info():
    """Fetches the approximate location (latitude, longitude, city, region, country)."""
    try:
        response = requests.get("https://ipinfo.io/json")
        data = response.json()

        loc = data.get("loc")  # Format: "latitude,longitude"
        city = data.get("city")
        region = data.get("region")
        country = data.get("country")

        if loc:
            latitude, longitude = loc.split(',')
            return {
                "latitude": latitude,
                "longitude": longitude,
                "city": city,
                "region": region,
                "country": country
            }
        else:
            return {"error": "Could not determine location"}

    except requests.RequestException as e:
        return {"error": f"Error fetching location: {e}"}

# Define the bottom third of the frame
def is_in_bottom_third(bbox, height):
    """Check if the bounding box is in the bottom third of the frame."""
    _, y_max, _, _ = bbox
    return y_max > (height * 0.6)

# Track the time of the last screenshot
last_capture_time = 0
cooldown_period = 10  # cooldown period in seconds

while True:
    # Capture frame
    frame = picam2.capture_array()

    # Run detection
    results = model(frame, imgsz=320)

    # Get the frame height and width
    height, width = frame.shape[:2]

    # Draw results (annotated frame)
    annotated_frame = results[0].plot()

    # Get location information
    location_info = get_location_info()
    
    # Format the location information into a readable string
    if "error" in location_info:
        location_text = location_info["error"]
    else:
        location_text = f"{location_info['city']}, {location_info['region']}, {location_info['country']} - " \
                         f"Lat: {location_info['latitude']}, Lon: {location_info['longitude']}"

    # Display location info on the frame
    cv2.putText(annotated_frame, location_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1, cv2.LINE_AA)
    
    # Get the current time when the screenshot is taken
    current_time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Display time below the location text
    cv2.putText(annotated_frame, f"Time: {current_time_str}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1, cv2.LINE_AA)



    # Process detections
    for obj in results[0].boxes.data:  # Each detection
        cls_id = int(obj[5])  # Class ID (person is typically class 0)
        if cls_id == 0:  # Person class ID
            # Get the bounding box coordinates (x1, y1, x2, y2)
            bbox = obj[:4].tolist()

            # Check if the bounding box is in the bottom third of the frame
            if is_in_bottom_third(bbox, height):
                # Check if enough time has passed since the last capture
                current_time = time.time()
                if current_time - last_capture_time >= cooldown_period:
                    # Capture the image when a person is detected in the bottom third
                    timestamp = cv2.getTickCount()
                    photo_filename = f"Screenshot-dump/photo_{timestamp}.jpg"
                    cv2.imwrite(photo_filename, annotated_frame)  # Save the frame as a photo
                    print(f"Photo captured: {photo_filename}")

                    # Update the last capture time
                    last_capture_time = current_time
                else:
                    print("Cooldown period active. Skipping capture.")

    
    # Display the frame
    cv2.imshow("YOLO Person Detection", annotated_frame)

    # Exit loop on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Clean up
cv2.destroyAllWindows()
picam2.stop()

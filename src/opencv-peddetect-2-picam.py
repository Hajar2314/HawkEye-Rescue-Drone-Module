import cv2
from picamera2 import Picamera2

# Initialize HOG person detector
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

# Initialize Pi Camera
picam2 = Picamera2()
picam2.configure(
    picam2.create_preview_configuration(
        main={"format": "BGR888"}
    )
)
picam2.start()

while True:
    # Capture frame from camera
    frame = picam2.capture_array()

    # Resize for faster processing
    height, width = frame.shape[:2]
    new_width = min(400, width)
    scale = new_width / float(width)
    new_height = int(height * scale)
    frame = cv2.resize(frame, (new_width, new_height))


    # Convert to grayscale (faster detection)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect pedestrians
    (regions, _) = hog.detectMultiScale(
        gray,
        winStride=(4, 4),
        padding=(4, 4),
        scale=1.05
    )

    # Draw bounding boxes
    for (x, y, w, h) in regions:
        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            (0, 0, 255),
            2
        )

    # Show output
    cv2.imshow("Pi Camera - Person Detection", frame)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
picam2.stop()

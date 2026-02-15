import cv2
from ultralytics import YOLO

# -----------------------------
# Initialize camera using OpenCV
# -----------------------------
# 0 = default camera (libcamera)
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

# Optional: set resolution
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1280)

if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

# -----------------------------
# Load YOLOv8 model
# -----------------------------
model = YOLO("yolov8n.pt")  # make sure yolov8n.pt is in working directory

# -----------------------------
# Main loop
# -----------------------------
while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    # Run YOLO model
    results = model(frame)

    # Annotate frame with detections
    annotated_frame = results[0].plot()

    # Display FPS
    inference_time = results[0].speed['inference']
    fps = 1000 / inference_time  # Convert to milliseconds
    text = f'FPS: {fps:.1f}'
    font = cv2.FONT_HERSHEY_SIMPLEX
    text_size = cv2.getTextSize(text, font, 1, 2)[0]
    text_x = annotated_frame.shape[1] - text_size[0] - 10
    text_y = text_size[1] + 10
    cv2.putText(annotated_frame, text, (text_x, text_y), font, 1, (255, 255, 255), 2, csudo rm /usr/local/bin/python3.13v2.LINE_AA)

    # Show the frame
    cv2.imshow("Camera", annotated_frame)

    # Exit on 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# -----------------------------
# Cleanup
# -----------------------------
cap.release()
cv2.destroyAllWindows()


# import cv2
# from picamera2 import Picamera2
# from ultralytics import YOLO
# 
# # Set up the camera with Picam
# picam2 = Picamera2()
# picam2.preview_configuration.main.size = (1280, 1280)
# picam2.preview_configuration.main.format = "RGB888"
# picam2.preview_configuration.align()
# picam2.configure("preview")
# picam2.start()
# 
# # Load YOLOv8
# model = YOLO("yolov8n.pt")
# 
# while True:
#     # Capture a frame from the camera
#     frame = picam2.capture_array()
#     
#     # Run YOLO model on the captured frame and store the results
#     results = model(frame)
#     
#     # Output the visual detection data, we will draw this on our camera preview window
#     annotated_frame = results[0].plot()
#     
#     # Get inference time
#     inference_time = results[0].speed['inference']
#     fps = 1000 / inference_time  # Convert to milliseconds
#     text = f'FPS: {fps:.1f}'
# 
#     # Define font and position
#     font = cv2.FONT_HERSHEY_SIMPLEX
#     text_size = cv2.getTextSize(text, font, 1, 2)[0]
#     text_x = annotated_frame.shape[1] - text_size[0] - 10  # 10 pixels from the right
#     text_y = text_size[1] + 10  # 10 pixels from the top
# 
#     # Draw the text on the annotated frame
#     cv2.putText(annotated_frame, text, (text_x, text_y), font, 1, (255, 255, 255), 2, cv2.LINE_AA)
# 
#     # Display the resulting frame
#     cv2.imshow("Camera", annotated_frame)
# 
#     # Exit the program if q is pressed
#     if cv2.waitKey(1) == ord("q"):
#         break
# 
# # Close all windows
# cv2.destroyAllWindows()
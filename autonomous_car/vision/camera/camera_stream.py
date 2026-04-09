import cv2
import numpy as np

PIPELINE = (
    "libcamerasrc ! "
    "video/x-raw,width=720,height=576,format=RGB ! "
    "videoconvert ! appsink drop=true max-buffers=1"
)

cap = cv2.VideoCapture(PIPELINE, cv2.CAP_GSTREAMER)

if not cap.isOpened():
    print("❌ Camera not opened")
    exit(1)     
    
print("✅ Camera opened. Press 'q' to quit.")


while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Frame not received")
        break

    cv2.imshow("Camera Stream", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
cap.release()
cv2.destroyAllWindows()
import cv2

PIPELINE = (
    "libcamerasrc ! "
    "video/x-raw,width=640,height=480 ! "
    "videoconvert ! video/x-raw,format=RGB ! "
    "appsink"
)

cap = cv2.VideoCapture(PIPELINE, cv2.CAP_GSTREAMER)

print("Opened:", cap.isOpened())

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Frame failed")
        break

    cv2.imshow("Test", frame)
    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()
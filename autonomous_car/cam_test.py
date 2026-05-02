import cv2

pipeline = (
    "libcamerasrc ! "
    "video/x-raw,width=640,height=480, format=YUY2, framerate=30/1 ! "
    "queue max-size-buffers=1 leaky=downstream !"
    "videoconvert ! "
    "video/x-raw,format=BGR ! "
    "appsink drop=true max-buffers=1 sync=false"
)

cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)

if not cap.isOpened():
    print("Camera failed")
    exit()

print("Camera started... Press ESC to exit")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Frame not received")
        break

    cv2.imshow("Test", frame)

    key = cv2.waitKey(1)
    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()



####    TEST - 02     #####
# import cv2

# pipeline = (
#     "libcamerasrc ! "
#     "video/x-raw,width=640,height=480,format=NV12,framerate=30/1 ! "
#     "queue max-size-buffers=1 leaky=downstream ! "
#     "appsink drop=true max-buffers=1 sync=false"
# )

# cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)

# if not cap.isOpened():
#     print("Camera failed")
#     exit()

# print("Low-latency camera running...")

# while True:
#     ret, frame = cap.read()
#     frame = cv2.cvtColor(frame, cv2.COLOR_YUV2BGR_NV12)
#     if not ret:
#         break

#     cv2.imshow("Test", frame)

#     if cv2.waitKey(1) == 27:
#         break

# cap.release()
# cv2.destroyAllWindows()




###### TEST -- 03 ######

# import cv2
# import threading

# class Camera:
#     def __init__(self):
#         self.cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
#         self.ret, self.frame = self.cap.read()
#         self.running = True
#         threading.Thread(target=self.update, daemon=True).start()

#     def update(self):
#         while self.running:
#             self.ret, self.frame = self.cap.read()

#     def read(self):
#         return self.frame

#     def stop(self):
#         self.running = False
#         self.cap.release()


# cam = Camera()

# while True:
#     frame = cam.read()
#     cv2.imshow("Test", frame)

#     if cv2.waitKey(1) == 27:
#         break

# cam.stop()
# cv2.destroyAllWindows()
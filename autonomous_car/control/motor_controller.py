import cv2
import numpy as np
import serial
import time

# ---------------- SERIAL ----------------
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
time.sleep(2)
print("[INFO] Arduino Connected")

# ---------------- CAMERA ----------------
PIPELINE = (
    "libcamerasrc ! "
    "video/x-raw,width=640,height=480,format=RGB, framerate=30/1 ! "
    "videoconvert ! "
    "appsink drop=true max-buffers=1 sync=false"
)

cap = cv2.VideoCapture(PIPELINE, cv2.CAP_GSTREAMER)

if not cap.isOpened():
    print("❌ Camera error")
    exit()

print("✅ Camera ready")

# ---------------- PARAMETERS ----------------
DEAD_ZONE = 25
ALPHA = 0.2
CONTROL_INTERVAL = 0.05
STARTUP_DELAY = 3   # 👈 important

last_time = 0
start_time = time.time()

smooth_error = None
last_cmd = None

# ---------------- FUNCTION ----------------
def send_cmd(cmd):
    global last_cmd
    if cmd != last_cmd:
        ser.write(cmd.encode())
        last_cmd = cmd
        print("CMD:", cmd)

# ---------------- MAIN LOOP ----------------
while True:
    ret, frame = cap.read()
    if not ret:
        continue

    h, w, _ = frame.shape
    center_x = w // 2

    # 🟡 STARTUP STABILIZATION
    if time.time() - start_time < STARTUP_DELAY:
        send_cmd('S')
        cv2.putText(frame, "Stabilizing...",
                    (20, 40), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0, 0, 255), 2)
        cv2.imshow("Frame", frame)
        cv2.waitKey(1)
        continue

    # 🟡 RATE LIMIT
    now = time.time()
    if now - last_time < CONTROL_INTERVAL:
        continue
    last_time = now

    # -------- PROCESS --------
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 150)

    roi_top = int(h * 0.1)
    roi_bottom = int(h * 0.65)
    roi = edges[roi_top:roi_bottom, :]

    ys, xs = np.where(roi > 0)

    if len(xs) > 0:
        lane_center = int(np.mean(xs))
        raw_error = lane_center - center_x

        # 🔵 SMOOTHING
        if smooth_error is None:
            smooth_error = raw_error
        else:
            smooth_error = int(ALPHA * raw_error + (1 - ALPHA) * smooth_error)

        error = smooth_error

        # -------- DECISION --------
        if abs(error) < DEAD_ZONE:
            cmd = 'F'
        elif error > DEAD_ZONE:
            cmd = 'R'
        else:
            cmd = 'L'

        send_cmd(cmd)

        # -------- VISUAL --------
        draw_y = roi_top + (roi_bottom - roi_top)//2
        cv2.circle(frame, (lane_center, draw_y), 5, (0,0,255), -1)
        cv2.line(frame, (center_x,0),(center_x,h),(255,0,0),1)

        cv2.putText(frame, f"Error: {error}",
                    (20,40), cv2.FONT_HERSHEY_SIMPLEX,
                    1,(0,255,0),2)

    else:
        send_cmd('S')
        smooth_error = None
        cv2.putText(frame, "Lane Lost",
                    (20,40), cv2.FONT_HERSHEY_SIMPLEX,
                    1,(0,0,255),2)

    cv2.imshow("Frame", frame)
    cv2.imshow("ROI", roi)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ---------------- CLEANUP ----------------
send_cmd('S')
cap.release()
cv2.destroyAllWindows()
ser.close()
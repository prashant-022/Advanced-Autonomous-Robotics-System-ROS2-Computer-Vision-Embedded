import cv2
import numpy as np
import serial
import time
from collections import deque

# ---------------- SERIAL SETUP ----------------
SERIAL_PORT = "/dev/ttyACM0"
BAUD_RATE = 9600

ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
time.sleep(2)  # wait for Arduino
print("[INFO] Connected to Arduino")

# ---------------- CAMERA SETUP ----------------
PIPELINE = (
    "libcamerasrc ! "
    "video/x-raw,width=640,height=480,format=RGB, framerate=30/1 ! "
    "videoconvert ! "
    "appsink drop=true max-buffers=1 sync=false"
)

cap = cv2.VideoCapture(PIPELINE, cv2.CAP_GSTREAMER)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)

if not cap.isOpened():
    print("❌ Camera not opened")
    exit(1)

print("✅ Camera opened")

# ---------------- PARAMETERS ----------------
STEER_DEAD_ZONE = 25            # pixels
CONTROL_INTERVAL = 0.05         # 20 Hz
TURN_PULSE_TIME = 0.03          # seconds

ALPHA = 0.2                      # EMA smoothing factor
OBSTACLE_AREA_THRESHOLD = 3000  # tune later

STARTUP_DELAY = 5.0             # seconds
LANE_LOST_FRAMES = 3

# ---------------- STATE VARIABLES ----------------
last_cmd = None
last_control_time = 0
start_time = time.time()

smooth_error = None
lane_lost_count = 0


# ---------------- FUNCTIONS ----------------
def send_cmd(cmd):
    global last_cmd
    if cmd != last_cmd:
        ser.write(cmd.encode())
        last_cmd = cmd
        print(f"[CMD] {cmd}")

def detect_obstacle(edges, h, w):
    roi = edges[int(h*0.6):h, int(w*0.3):int(w*0.7)]
    area = np.count_nonzero(roi)
    return area > OBSTACLE_AREA_THRESHOLD

# ---------------- MAIN LOOP ----------------
while True:
    cap.grab()
    cap.grab()
    
    ret, frame = cap.read()
    if not ret:
        continue

    h, w, _ = frame.shape
    center_x = w // 2
    
    # ---------- STARTUP STABILIZATION ----------
    if time.time() - start_time < STARTUP_DELAY:
        cv2.putText(
            frame, "Stabilizing...",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1, (0, 0, 255), 2)
        
        cv2.imshow("Lane Control", frame)
        cv2.waitKey(1)
        continue

# ---------- RATE LIMIT ----------
    now = time.time()
    if now - last_control_time < CONTROL_INTERVAL:
        continue
    last_control_time = now

    # ----- Preprocess -----
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 150)

    # ----- ROI -----
    roi_top = int(h * 0.10)
    roi_bottom = int(h * 0.65)
    roi = edges[roi_top:roi_bottom, :]

    # ----- Find lane pixels -----
    ys, xs = np.where(roi > 0)

    if len(xs) > 0:
        lane_lost_count = 0
        lane_center = int(np.mean(xs))
        raw_error = lane_center - center_x
        
        # ----- Smooth error -----
        if smooth_error is None:
            smooth_error = raw_error
        else:
            smooth_error = int(ALPHA * raw_error + (1 - ALPHA) * smooth_error)
        
        lane_error = smooth_error

        # --------- Visuals ---------
        draw_y = roi_top + (roi_bottom - roi_top) // 2
        cv2.circle(frame, (lane_center, draw_y), 6, (0, 0, 255), -1)
        cv2.line(frame, (center_x, 0), (center_x, h), (255, 0, 0), 1)
        cv2.putText(frame, f"Lane error: {lane_error}px",
                    (20, 40), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0, 255, 0), 2)

        # ----- Obstacle check -----
        if detect_obstacle(edges, h, w):
            send_cmd('S')

        else:
            # ----- Steering Control -----
            if abs(lane_error) < STEER_DEAD_ZONE:
                send_cmd('F')
                
            elif lane_error > STEER_DEAD_ZONE:
                send_cmd('R')
                time.sleep(TURN_PULSE_TIME)
                send_cmd('F') 

            elif lane_error < -STEER_DEAD_ZONE:
                send_cmd('L')
                time.sleep(TURN_PULSE_TIME)
                send_cmd('F')
                

    else:
        lane_lost_count += 1
        if lane_lost_count >= LANE_LOST_FRAMES:
            send_cmd('S')
            smooth_error = None  # reset smoothing
            cv2.putText(frame, "Lane lost",
                    (20, 40), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0, 0, 255), 2)

    # ----- Display -----
    cv2.imshow("Lane Control", frame)
    cv2.imshow("Edges", edges)
    cv2.imshow("ROI", roi)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ---------------- CLEANUP ----------------
send_cmd('S')
cap.release()
cv2.destroyAllWindows()
ser.close()
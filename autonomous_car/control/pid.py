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
    "video/x-raw,width=640,height=480, format=YUY2, framerate=30/1 ! "
    "videoconvert ! "
    "video/x-raw,format=BGR ! "
    "appsink drop=true max-buffers=1 sync=false"
)

cap = cv2.VideoCapture(PIPELINE, cv2.CAP_GSTREAMER)

if not cap.isOpened():
    print("Camera error")
    exit()

print("Camera ready")

# ---------------- PARAMETERS ----------------
## Camera Parameters
STARTUP_DELAY = 3
start_time = time.time()

## Control Parameters
DEAD_ZONE = 40
ALPHA = 0.2
CONTROL_INTERVAL = 0.02
last_time = 0
smooth_error = None
last_cmd = None
last_left = 0
last_right = 0

# PID Parameters
Kp = 0.01
Kd = 0.001
Ki = 0.0

prev_error = 0
integral = 0

# ---------------- MAIN LOOP ----------------
while True:
    ret, frame = cap.read()
    if not ret:
        continue

    ## fast color conversion:
    # frame = cv2.cvtColor(frame, cv2.COLOR_YUV2BGR_YUYV)
    
    ## Resizing
    # frame = cv2.resize(frame, (320, 240))

    h, w, _ = frame.shape
    center_x = w // 2

    # STARTUP STABILIZATION
    if time.time() - start_time < STARTUP_DELAY:
        ser.write(b"0,0\n")
        cv2.putText(frame, "Stabilizing...",
                    (20, 40), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0, 0, 255), 2)
        # cv2.imshow("Frame", frame)
        cv2.waitKey(1)
        continue

    # RATE LIMIT
    now = time.time()
    if now - last_time < CONTROL_INTERVAL:
        # still send last command to keep Arduino alive
        cmd = f"{last_left},{last_right}\n"
        ser.write(cmd.encode())
        continue
    last_time = now

    # -------- PROCESS --------
    
    roi_top = int(h * 0.1)
    roi_bottom = int(h * 0.65)
    roi_frame = frame[roi_top:roi_bottom, :]
    
    gray = cv2.cvtColor(roi_frame, cv2.COLOR_BGR2GRAY)
    # blur = cv2.GaussianBlur(gray, (5, 5), 0)      ## Avoiding this increase the speed.
    
    edges = cv2.Canny(gray, 50, 150)

    # ys, xs = np.where(roi_gray > 0)
    hist = np.sum(edges, axis=0)             ### Updated for fast calculations

    if np.max(hist) > 0:
        # lane_center = int(np.mean(xs))
        lane_center = int(np.argmax(hist))     ### Updated for fast calculations
        raw_error = lane_center - center_x

        # SMOOTHING
        if smooth_error is None:
            smooth_error = raw_error
        else:
            smooth_error = int(ALPHA * raw_error + (1 - ALPHA) * smooth_error)

        error = smooth_error

        # -------- DECISION --------
        dt = CONTROL_INTERVAL
        
        # PID
        integral += error * dt
        derivative = (error - prev_error) / dt
        
        output = Kp * error + Ki * integral + Kd * derivative
        
        prev_error = error
        
        # Convert to motor speeds
        base_speed = 140
        correction = int(output)
        
        if abs(correction) < 5:
            correction = 0
        
        # Limit max correction
        max_correction = 40
        correction = max(-max_correction, min(max_correction, correction))
        
        left_speed = base_speed - correction
        right_speed = base_speed + correction
        
        # Clamp
        left_speed = max(0, min(255, left_speed))
        right_speed = max(0, min(255, right_speed))
        
        # Motor Smoothing
        alpha_motor = 0.7
        
        if 'prev_left' not in globals():
            prev_left = left_speed
            prev_right = right_speed
            
        left_speed = int(alpha_motor * prev_left + (1 - alpha_motor) * left_speed)
        right_speed = int(alpha_motor * prev_right + (1 - alpha_motor) * right_speed)
        
        prev_left = left_speed
        prev_right = right_speed
        
        last_left = left_speed
        last_right = right_speed
        
        # Send as custom command
        cmd = f"{left_speed},{right_speed}\n"
        ser.write(cmd.encode())
        
        print(f"L:{left_speed} R:{right_speed} Error:{error}")


        # -------- VISUAL --------
        draw_y = roi_top + (roi_bottom - roi_top)//2
        cv2.circle(roi_frame, (lane_center, draw_y), 5, (0,0,255), -1)
        cv2.line(frame, (center_x,0),(center_x,h),(255,0,0),1)

        cv2.putText(frame, f"Error: {error}",
                    (20,40), cv2.FONT_HERSHEY_SIMPLEX,
                    1,(0,255,0),2)

    else:
        ser.write(b"0,0\n")
        smooth_error = None
        cv2.putText(frame, "Lane Lost",
                    (20,40), cv2.FONT_HERSHEY_SIMPLEX,
                    1,(0,0,255),2)

    # cv2.imshow("Frame", frame)
    # cv2.imshow("ROI", roi_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ---------------- CLEANUP ----------------
ser.write(b"0,0\n")
time.sleep(0.1)
cap.release()
cv2.destroyAllWindows()
ser.close() 
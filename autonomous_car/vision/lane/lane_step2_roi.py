import cv2
import numpy as np

# -------------------------------
# Camera pipeline (Pi 5 + libcamera)
# -------------------------------
PIPELINE = (
    "libcamerasrc ! "
    "video/x-raw,width=640,height=480, format=YUY2, framerate=30/1 ! "
    "videoconvert ! "
    "video/x-raw,format=BGR ! "
    "appsink drop=true max-buffers=1 sync=false"
)

cap = cv2.VideoCapture(PIPELINE, cv2.CAP_GSTREAMER)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)

if not cap.isOpened():
    print("❌ Camera not opened")
    exit(1)

print("✅ Camera opened. Press 'q' to quit.")

# -------------------------------
# Main loop
# -------------------------------
while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Frame not received")
        break

    h, w, _ = frame.shape

    # -------------------------------
    # 1. Preprocess
    # -------------------------------
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 150)

    # -------------------------------
    # 2. ROI (important)
    # -------------------------------
    roi_top = int(h * 0.10)
    roi_bottom = int(h * 0.65)

    roi = edges[roi_top:roi_bottom, :]

    # Draw ROI on original image
    cv2.rectangle(
        frame,
        (0, roi_top),
        (w, roi_bottom),
        (0, 255, 0),
        2
    )

    # -------------------------------
    # 3. Split ROI into left & right
    # -------------------------------
    roi_h, roi_w = roi.shape
    mid_x = roi_w // 2

    left_half = roi[:, :mid_x]
    right_half = roi[:, mid_x:]

    # -------------------------------
    # 4. Find INNER edges
    # -------------------------------
    left_inner_x = None
    right_inner_x = None

    ys, xs = np.where(left_half > 0)
    if len(xs) > 0:
        left_inner_x = np.max(xs)

    ys, xs = np.where(right_half > 0)
    if len(xs) > 0:
        right_inner_x = np.min(xs) + mid_x

    # -------------------------------
    # 5. Compute lane center
    # -------------------------------
    if left_inner_x is not None and right_inner_x is not None:
        lane_center_x = (left_inner_x + right_inner_x) // 2
        center_y = roi_top + roi_h // 2

        # Draw center dot
        cv2.circle(frame, (lane_center_x, center_y), 6, (0, 0, 255), -1)

        # Draw helper lines
        cv2.line(frame, (left_inner_x, roi_top), (left_inner_x, roi_bottom), (255, 0, 0), 2)
        cv2.line(frame, (right_inner_x, roi_top), (right_inner_x, roi_bottom), (255, 0, 0), 2)

        # Lane error (for control later)
        car_center_x = w // 2
        error_px = lane_center_x - car_center_x

        cv2.putText(
            frame,
            f"Lane error: {error_px}px",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

    else:
        cv2.putText(
            frame,
            "Lane not detected",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 255),
            2
        )

    # -------------------------------
    # 6. Show windows
    # -------------------------------
    cv2.imshow("Original (on rpi5)", frame)
    cv2.imshow("Edges (on rpi5)", edges)
    cv2.imshow("ROI (on rpi5)", roi)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# -------------------------------
# Cleanup
# -------------------------------
cap.release()
cv2.destroyAllWindows()
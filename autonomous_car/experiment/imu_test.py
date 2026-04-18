import smbus
import time
import math

bus = smbus.SMBus(1)
MPU_ADDR = 0x68

# Wake up MPU6050
bus.write_byte_data(MPU_ADDR, 0x6B, 0)

def read_word(reg):
    high = bus.read_byte_data(MPU_ADDR, reg)
    low = bus.read_byte_data(MPU_ADDR, reg+1)
    value = (high << 8) + low
    if value >= 0x8000:
        value = -((65535 - value) + 1)
    return value

def get_accel():
    ax = read_word(0x3B) / 16384.0
    ay = read_word(0x3D) / 16384.0
    az = read_word(0x3F) / 16384.0
    return ax, ay, az

def get_gyro():
    gx = read_word(0x43) / 131.0
    gy = read_word(0x45) / 131.0
    gz = read_word(0x47) / 131.0
    return gx, gy, gz

## Calibration and filtering parameters
print("Calibrating... Keep robot still")

gx_offset = gy_offset = gz_offset = 0
samples = 500

for _ in range(samples):
    gx, gy, gz = get_gyro()
    gx_offset += gx
    gy_offset += gy
    gz_offset += gz
    time.sleep(0.005)

gx_offset /= samples
gy_offset /= samples
gz_offset /= samples

print(f"Gyro Offset: {gx_offset:.3f}, {gy_offset:.3f}, {gz_offset:.3f}")

## Initialize
ax, ay, az = get_accel()
angle = math.atan2(ay, az)      ## radians
yaw = 0

alpha = 0.98
prev_time = time.time()

file = open("imu_data.txt", "w")

## Loop:
while True:
    current_time = time.time()
    dt = current_time - prev_time
    prev_time = current_time
    
    if dt <= 0 or dt > 0.1:
        continue 
    
    ## Clamp dt:
    dt = min(dt, 0.05)
    
    ax, ay, az = get_accel()
    gx, gy, gz = get_gyro()
    
    gx -= gx_offset
    gy -= gy_offset
    gz -= gz_offset
    
    ## Small noise removal:
    if abs(gz) < 0.5:
        gz = 0
    
    ## Convert to radians:
    gx_rad = math.radians(gx)
    gz_rad = math.radians(gz)
    
    yaw += gz * dt
    
    ## Acc angle:
    acc_angle = math.atan2(ay, az)
    
    ## Complementary filter:
    gyro_angle = angle + gx_rad * dt
    angle = alpha * gyro_angle + (1-alpha) * acc_angle

    # print(f"Angle(deg): {math.degrees(angle):.2f} | Yaw(deg): {yaw:.2f}")
    output = f"Angle(deg): {math.degrees(angle):.2f} | Yaw(deg): {yaw:.2f}"
    print(output)
    file.write(output + "\n")
    file.flush()

    time.sleep(0.02)
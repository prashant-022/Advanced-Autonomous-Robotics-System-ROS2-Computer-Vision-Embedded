# Arduino Firmware


### Compiling and Uploading code directly from RPi 5 terminal to Arduino Uno board:
- Compiling:
```
arduino-cli compile --fqbn arduino:avr:uno motor_driver.ino
```
- Uploading:
```
arduino-cli upload -p /dev/ttyACM0 --fqbn arduino:avr:uno motor_driver.ino
```

## Components used:
1. Arduino UNO
2. Raspberry Pi 5 (4GB RAM, 64GB SD Card) with Raspberry Pi 5 Active Cooler.
3. Motor driver: Motor Driver TB6612FNG Module Performance Ultra Small Volume 3 PI Matching Performance Ultra L298N
4. Motor: TT Motor - N20 12V 135RPM Metal gear Motor With Encoder D type
5. Battery: combination of 18650 cells (3.7V, 2200mAh)
6. Wheels: 
7. Sensors:
    - Camera: Raspberry Pi 5MP Camera Module
    - IMU: MPU-6050 Triple-Axis Accelerometer & Gyroscope Module

## Motor driver pins and connection:
```
VM  -> (+) of battery                      |  PWMA -> digital pin 10 of arduino
VCC -> 5V pin of arduino                   |  AIN2 -> digital pin 9 of arduino
GND -> (-) of battery                      |  AIN1 -> digital pin 8 of arduino
A01 -> (+) of two left motors, common      |  STBY -> digital pin 7 of arduino
A02 -> (-) of two left motors, common      |  BIN1 -> digital pin 11 of arduino
B02 -> (+) of two right motors, common     |  BIN2 -> digital pin 12 of arduino
B01 -> (-) of two right motors, common     |  PWMB -> digital pin 5 of arduino
GND -> gnd of arduino                      |  GND -> Not connected
```

## Encoder connection with arduino (with hardware limitations):
1. Two left encoders are connected together (their + and - terminals), same for right encoders.
2. One encoder's wires of left and one of right is connected to the arduino uno.
3. Encoder wire specifications:
- Red: (+) of motor
- Black: (-) of motor
- Green: Ground
- Brown: VCC
- Blue: A
- Purple: B

4. Right encoder motor (only one motor) connection:
- green -> gnd
- brown -> 5V pin of arduino
- A -> digital pin 2 of arduino
- B -> digital pin 3 of arduino 

5. Left encoder motor (only one motor) connection:
- green -> gnd
- brown -> 5V pin of arduino
- A -> digital pin 4 of arduino 
- B -> digital pin 6 of arduino

## Encoder testing (Ticks per Revolution):
```
Iteration-1

Right encoder Reading      | Left encoder reading  (Double of right)            
0                          | 0
347                        | 696
696                        | 1392
1046                       | 2091
1399                       | 3491
1748                       | 4188

Iteration-2:

Right encoder Reading      | Left encoder reading  (After fix)            
0                          | 0
350                        | 353
699                        | 706
1053                       | 1057
1396                       | 1406
1748                       | 1755
```



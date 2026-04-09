#define STBY 7

#define AIN1 8
#define AIN2 9
#define PWMA 10

#define BIN1 11
#define BIN2 12
#define PWMB 5

String inputString = "";
bool stringComplete = false;
unsigned long lastCommandTime = 0;
const int TIMEOUT = 1000;  // milliseconds

void setup() {
  Serial.begin(9600);

  pinMode(STBY, OUTPUT);
  pinMode(AIN1, OUTPUT);
  pinMode(AIN2, OUTPUT);
  pinMode(BIN1, OUTPUT);
  pinMode(BIN2, OUTPUT);
  pinMode(PWMA, OUTPUT);
  pinMode(PWMB, OUTPUT);

  digitalWrite(STBY, HIGH);

  stopMotors();

  inputString.reserve(20);
}

// ---------------- MAIN LOOP ----------------
void loop() {
  if (stringComplete) {
    processInput(inputString);
    inputString = "";
    stringComplete = false;
  }

  // SAFETY STOP
  if (millis() - lastCommandTime > TIMEOUT) {
    stopMotors();
  }
}

// ---------------- SERIAL EVENT ----------------
void serialEvent() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();

    if (inChar == '\n') {
      stringComplete = true;
    } else {
      inputString += inChar;
    }
  }
}

// ---------------- PROCESS INPUT ----------------
void processInput(String data) {
  int commaIndex = data.indexOf(',');

  if (commaIndex > 0) {
    int leftSpeed = data.substring(0, commaIndex).toInt();
    int rightSpeed = data.substring(commaIndex + 1).toInt();

    setMotor(leftSpeed, rightSpeed);

    lastCommandTime = millis();

    Serial.print("L:");
    Serial.print(leftSpeed);
    Serial.print(" R:");
    Serial.println(rightSpeed);
  }
}

// ---------------- MOTOR CONTROL ----------------
void setMotor(int left, int right) {
  // Forward direction (you can expand later)
  digitalWrite(AIN1, HIGH);
  digitalWrite(AIN2, LOW);
  digitalWrite(BIN1, HIGH);
  digitalWrite(BIN2, LOW);

  // Clamp safety
  left = constrain(left, 0, 255);
  right = constrain(right, 0, 255);

  analogWrite(PWMA, left);
  analogWrite(PWMB, right);
}

// ---------------- STOP ----------------
void stopMotors() {
  analogWrite(PWMA, 0);
  analogWrite(PWMB, 0);
}
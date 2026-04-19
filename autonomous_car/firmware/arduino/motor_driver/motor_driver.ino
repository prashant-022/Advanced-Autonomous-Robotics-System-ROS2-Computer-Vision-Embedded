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
volatile long right_ticks = 0;
long left_ticks = 0;

int prev_left_A = 0;
int prev_left_B = 0;

void setup() {
  Serial.begin(9600);

  left_ticks = 0;
  right_ticks = 0;

  pinMode(STBY, OUTPUT);
  pinMode(AIN1, OUTPUT);
  pinMode(AIN2, OUTPUT);
  pinMode(BIN1, OUTPUT);
  pinMode(BIN2, OUTPUT);
  pinMode(PWMA, OUTPUT);
  pinMode(PWMB, OUTPUT);

  pinMode(2, INPUT);
  pinMode(3, INPUT);

  pinMode(4, INPUT);
  pinMode(6, INPUT);

  attachInterrupt(digitalPinToInterrupt(2), rightEncoderISR, RISING);

  digitalWrite(STBY, HIGH);

  stopMotors();

  inputString.reserve(20);
}

// ---------------- MAIN LOOP ----------------
void loop() {
  int left_A = digitalRead(4);
  int left_B = digitalRead(6);

  if (left_A == HIGH && prev_left_A == LOW) {
    if (left_A == left_B) {
      left_ticks++;
    } else {
      left_ticks--;
    }
  }

  prev_left_A = left_A;
  prev_left_B = left_B;

  if (stringComplete) {
    processInput(inputString);
    inputString = "";
    stringComplete = false;
  }

  // SAFETY STOP
  if (millis() - lastCommandTime > TIMEOUT) {
    stopMotors();
  }

  static unsigned long lastPrint = 0;
  
  if (millis() - lastPrint > 200) {
    Serial.print(left_ticks);
    Serial.print(",");
    Serial.println(right_ticks);
    lastPrint = millis();
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

  data.trim();

  // -------- RESET COMMAND --------
  if (data == "RESET") {
    left_ticks = 0;
    right_ticks = 0;

    Serial.println("ENC RESET");
    return;
  }

  // -------- MOTOR COMMAND --------
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

  // LEFT MOTOR
  if (left >= 0) {
    digitalWrite(AIN1, HIGH);
    digitalWrite(AIN2, LOW);
  } else {
    digitalWrite(AIN1, LOW);
    digitalWrite(AIN2, HIGH);
    left = -left;
  }

  // RIGHT MOTOR
  if (right >= 0) {
    digitalWrite(BIN1, HIGH);
    digitalWrite(BIN2, LOW);
  } else {
    digitalWrite(BIN1, LOW);
    digitalWrite(BIN2, HIGH);
    right = -right;
  }

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

void rightEncoderISR() {
  int A = digitalRead(2);
  int B = digitalRead(3);

  if (A == B) {
    right_ticks++;
  } else {
    right_ticks--;
  }
}
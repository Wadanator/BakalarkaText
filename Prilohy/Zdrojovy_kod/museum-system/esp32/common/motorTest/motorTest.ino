// Motor PWM Control — 20 kHz with smooth ramp, compatible with Arduino Core 2.x and 3.x
// Serial commands: ON, OFF, L, R, 0–100 (speed %)

// Pin definitions
#define PWM_LEFT_PIN 27      // PWM pin for left direction
#define PWM_RIGHT_PIN 26     // PWM pin for right direction
#define ENABLE_PIN 25        // Enable pin for motor driver

// Smooth ramp settings
#define SMOOTH_STEP 2        // Speed increment per tick
#define SMOOTH_DELAY 20      // Milliseconds between ticks
#define PWM_FREQUENCY 20000  // 20 kHz PWM frequency
#define PWM_RESOLUTION 8     // 8-bit resolution (0–255)

// PWM channel assignments
#define PWM_LEFT_CHANNEL 0
#define PWM_RIGHT_CHANNEL 1

// State variables
int motorSpeed = 0;
int currentSpeed = 0;
char motorDirection = 'S';
char currentDirection = 'S';
bool motorEnabled = false;
unsigned long lastUpdate = 0;
bool systemReady = false;

void setup() {
  Serial.begin(115200);
  delay(100);
  Serial.println("=== MOTOR PWM CONTROL INIT ===");

  // Set all pins as outputs and drive them low
  pinMode(PWM_LEFT_PIN, OUTPUT);
  pinMode(PWM_RIGHT_PIN, OUTPUT);
  pinMode(ENABLE_PIN, OUTPUT);

  digitalWrite(PWM_LEFT_PIN, LOW);
  digitalWrite(PWM_RIGHT_PIN, LOW);
  digitalWrite(ENABLE_PIN, LOW);

  Serial.println("Pins configured and disabled");

  if (!setupPWMFrequency()) {
    Serial.println("ERROR: Failed to configure PWM!");
    while(1) delay(1000);
  }

  forceStopMotor();
  delay(100);
  testPWMChannels();

  systemReady = true;
  Serial.println("=== MOTOR PWM CONTROL 20kHz + SMOOTH ===");
  Serial.println("Commands:");
  Serial.println("  ON       - enable motor");
  Serial.println("  OFF      - disable motor");
  Serial.println("  L        - direction left");
  Serial.println("  R        - direction right");
  Serial.println("  0-100    - set speed (%)");
  Serial.println("  STATUS   - print current state");
  Serial.println("========================================");
  printStatus();
}

void loop() {
  if (!systemReady) {
    delay(100);
    return;
  }

  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');
    input.trim();
    input.toUpperCase();
    if (input.length() > 0) {
      processCommand(input);
    }
  }

  smoothMotorUpdate();
}

bool setupPWMFrequency() {
  Serial.println("Configuring PWM...");

  // ledcAttach returns configured frequency; works on both Core 2.x and 3.x
  double freq_left = ledcAttach(PWM_LEFT_PIN, PWM_FREQUENCY, PWM_RESOLUTION);
  if (freq_left == 0) {
    Serial.println("ERROR: Left PWM channel failed!");
    return false;
  }
  Serial.print("Left channel OK (");
  Serial.print(freq_left);
  Serial.println(" Hz)");

  double freq_right = ledcAttach(PWM_RIGHT_PIN, PWM_FREQUENCY, PWM_RESOLUTION);
  if (freq_right == 0) {
    Serial.println("ERROR: Right PWM channel failed!");
    return false;
  }
  Serial.print("Right channel OK (");
  Serial.print(freq_right);
  Serial.println(" Hz)");

  // Zero out both PWM channels
  ledcWrite(PWM_LEFT_PIN, 0);
  ledcWrite(PWM_RIGHT_PIN, 0);

  Serial.println("PWM configured successfully");
  return true;
}

void testPWMChannels() {
  Serial.println("Testing PWM channels...");

  ledcWrite(PWM_LEFT_PIN, 50);
  delay(100);
  ledcWrite(PWM_LEFT_PIN, 0);

  ledcWrite(PWM_RIGHT_PIN, 50);
  delay(100);
  ledcWrite(PWM_RIGHT_PIN, 0);

  Serial.println("PWM test complete");
}

void processCommand(String cmd) {
  Serial.print("Command: ");
  Serial.println(cmd);

  if (cmd == "ON") {
    motorEnabled = true;
    digitalWrite(ENABLE_PIN, HIGH);
    Serial.println("Motor ON");
  }
  else if (cmd == "OFF") {
    motorEnabled = false;
    motorSpeed = 0;
    Serial.println("Motor stopping...");
  }
  else if (cmd == "L") {
    if (motorDirection != 'L') {
      motorDirection = 'L';
      Serial.println("Direction: LEFT");
    }
  }
  else if (cmd == "R") {
    if (motorDirection != 'R') {
      motorDirection = 'R';
      Serial.println("Direction: RIGHT");
    }
  }
  else if (cmd == "STATUS") {
    printDetailedStatus();
    return;
  }
  else if (isNumeric(cmd)) {
    int speed = cmd.toInt();
    if (speed >= 0 && speed <= 100) {
      motorSpeed = speed;
      Serial.print("Target speed: ");
      Serial.print(motorSpeed);
      Serial.println("%");

      if (speed > 0 && !motorEnabled) {
        Serial.println("Auto-enabling motor...");
        motorEnabled = true;
        digitalWrite(ENABLE_PIN, HIGH);
      }
    } else {
      Serial.println("ERROR: Speed must be 0-100");
    }
  }
  else {
    Serial.println("ERROR: Unknown command");
    Serial.println("Valid commands: ON, OFF, L, R, 0-100, STATUS");
  }

  printStatus();
}

void smoothMotorUpdate() {
  unsigned long currentTime = millis();

  if (currentTime - lastUpdate < SMOOTH_DELAY) {
    return;
  }
  lastUpdate = currentTime;

  if (!motorEnabled) {
    if (currentSpeed > 0) {
      currentSpeed = max(0, currentSpeed - SMOOTH_STEP);
      updateMotorPWM();

      if (currentSpeed == 0) {
        digitalWrite(ENABLE_PIN, LOW);
        currentDirection = 'S';
        Serial.println("Motor OFF");
        printStatus();
      }
    }
    return;
  }

  if (motorDirection != currentDirection && currentSpeed > 0) {
    currentSpeed = max(0, currentSpeed - (SMOOTH_STEP * 2));
    updateMotorPWM();

    if (currentSpeed == 0) {
      currentDirection = motorDirection;
      Serial.print("Direction changed to: ");
      Serial.println(currentDirection == 'L' ? "LEFT" : "RIGHT");
    }
    return;
  }

  if (motorDirection != currentDirection && currentSpeed == 0) {
    currentDirection = motorDirection;
  }

  if (currentSpeed != motorSpeed) {
    int oldSpeed = currentSpeed;

    if (currentSpeed < motorSpeed) {
      currentSpeed = min(motorSpeed, currentSpeed + SMOOTH_STEP);
    } else {
      currentSpeed = max(motorSpeed, currentSpeed - SMOOTH_STEP);
    }

    if (oldSpeed != currentSpeed) {
      updateMotorPWM();
    }
  }
}

void updateMotorPWM() {
  if (currentSpeed == 0) {
    ledcWrite(PWM_LEFT_PIN, 0);
    ledcWrite(PWM_RIGHT_PIN, 0);
    return;
  }

  int pwmValue = map(currentSpeed, 0, 100, 0, 255);
  pwmValue = constrain(pwmValue, 0, 255);

  if (currentDirection == 'L') {
    ledcWrite(PWM_LEFT_PIN, pwmValue);
    ledcWrite(PWM_RIGHT_PIN, 0);
  }
  else if (currentDirection == 'R') {
    ledcWrite(PWM_LEFT_PIN, 0);
    ledcWrite(PWM_RIGHT_PIN, pwmValue);
  }
  else {
    ledcWrite(PWM_LEFT_PIN, 0);
    ledcWrite(PWM_RIGHT_PIN, 0);
  }
}

void forceStopMotor() {
  Serial.println("Emergency stop...");
  digitalWrite(ENABLE_PIN, LOW);
  ledcWrite(PWM_LEFT_PIN, 0);
  ledcWrite(PWM_RIGHT_PIN, 0);
  currentSpeed = 0;
  motorSpeed = 0;
  motorDirection = 'S';
  currentDirection = 'S';
  motorEnabled = false;
  Serial.println("Motor fully stopped");
}

void printStatus() {
  Serial.print("Status: ");
  Serial.print(motorEnabled ? "ON" : "OFF");
  Serial.print(" | Dir: ");

  switch(currentDirection) {
    case 'L': Serial.print("LEFT"); break;
    case 'R': Serial.print("RIGHT"); break;
    default: Serial.print("STOP"); break;
  }

  Serial.print(" | Current: ");
  Serial.print(currentSpeed);
  Serial.print("% | Target: ");
  Serial.print(motorSpeed);
  Serial.println("%");
  Serial.println("---");
}

void printDetailedStatus() {
  Serial.println("=== DETAILED STATUS ===");
  Serial.print("System: ");
  Serial.println(systemReady ? "READY" : "INITIALIZING");
  Serial.print("Motor: ");
  Serial.println(motorEnabled ? "ON" : "OFF");
  Serial.print("Enable pin (GPIO25): ");
  Serial.println(digitalRead(ENABLE_PIN) ? "HIGH" : "LOW");
  Serial.print("Current direction: ");
  Serial.println(currentDirection);
  Serial.print("Target direction: ");
  Serial.println(motorDirection);
  Serial.print("Current speed: ");
  Serial.print(currentSpeed);
  Serial.println("%");
  Serial.print("Target speed: ");
  Serial.print(motorSpeed);
  Serial.println("%");
  Serial.print("PWM frequency: ");
  Serial.print(PWM_FREQUENCY);
  Serial.println(" Hz");
  Serial.println("=====================");
}

bool isNumeric(String str) {
  if (str.length() == 0) return false;
  for (unsigned int i = 0; i < str.length(); i++) {
    if (!isDigit(str.charAt(i))) {
      return false;
    }
  }
  return true;
}

// Test sketch for verifying button wiring
// Wiring: 3.3V -> Resistor (6k–10k) -> Pin 32 -> Button -> GND

const int BUTTON_PIN = 32;

void setup() {
  Serial.begin(115200);
  delay(1000);

  // INPUT mode: external pull-up resistor to 3.3V
  pinMode(BUTTON_PIN, INPUT);
  
  Serial.println("--- Test stability tlacidla ---");
  Serial.println("Ocakavany stav: 1 (uvolnene), 0 (stlacene)");
}

void loop() {
  // Direct pin read — no debounce or cooldown
  int stav = digitalRead(BUTTON_PIN);

  Serial.print("Stav pinu 32: ");
  Serial.println(stav);

  if (stav == LOW) {
    Serial.println(">>> TLACIDLO ZOPNUTE <<<");
  }

  // Short delay to keep the serial output readable
  delay(100); 
}
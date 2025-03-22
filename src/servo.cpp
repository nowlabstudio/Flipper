#include <ESP32Servo.h>

Servo myservo;  
const int servoPin = 33;

// Szervo inicializálása
void servoInit() {
  myservo.setPeriodHertz(333);
  myservo.attach(servoPin, 900, 2100);  // 900µs - 2100µs impulzus tartomány
}

// Szervo mozgatása
void servo(int delayTime) {
  // 180-tól 0 fokig (először megy visszafelé)
  for(int pos = 176; pos >= 45; pos--) {  // 172 45
    myservo.write(pos);
    delay(1);
  }
  delay(300);
  
  // 0-tól 180 fokig (aztán megy előre)
  for(int pos = 45; pos <= 176; pos++) {  // 45 172
    myservo.write(pos);
    // delay(1);  
  }
  
  // Várakozás a következő mozgatás előtt
  delay(delayTime);
}
/*
 * Servo Controller Implementation
 * 
 * This file implements basic servo control functions:
 * - Initialization of ESP32 servo on specified pin
 * - Pattern-based servo movement (176� to 45� and back)
 * 
 * The servo movements are blocking, but the main code
 * only calls them at specific intervals (every 3 seconds)
 * and only when the system is in active state.
 */

#include <ESP32Servo.h>

Servo myservo;  
const int servoPin = 33;  // GPIO pin for servo control

// Initialize the servo
void servoInit() {
  // Set up timers for ESP32 Servo library
  ESP32PWM::allocateTimer(0);
  // ESP32PWM::allocateTimer(1);
  // ESP32PWM::allocateTimer(2);
  // ESP32PWM::allocateTimer(3);
  
  // Configure servo with 333Hz PWM frequency
  myservo.setPeriodHertz(333);
  
  // Attach servo with 900-2100�s pulse range
  myservo.attach(servoPin, 900, 2100);
}

// Move servo in a predefined pattern
void servo(int delayTime) {
  // First sweep: 176� to 45� (backward movement)
  for(int pos = 176; pos >= 45; pos--) {
    myservo.write(pos);
    delay(1);  // Small delay for smooth movement
  }
  delay(300);  // Pause at end position
  
  // Second sweep: 45� to 176� (forward movement)
  for(int pos = 45; pos <= 176; pos++) {
    myservo.write(pos);
    // No delay for faster movement
  }
  
  // Wait before next movement cycle
  delay(delayTime);
}
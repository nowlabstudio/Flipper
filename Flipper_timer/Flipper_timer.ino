/*
 * M5Core2 Servo Control with Simple Timers
 * ---------------------------------------
 * This program controls a servo motor connected to an M5Core2 device.
 * It sweeps the servo from one extreme position to another and back,
 * then powers off the device after a delay.
 * 
 * Added features:
 * - 10 second delay after power-on before servo movement begins
 * - 10 second delay before power-off after servo movement completes
 */

#include <M5Core2.h>       
#include <ESP32Servo.h>    

Servo myservo;             
const int servoPin = 33;   

void setup() {
  M5.begin();         
  
  ESP32PWM::allocateTimer(0);  
  myservo.setPeriodHertz(333);  
  
  // Attach the servo to the specified pin and set the pulse width range
  // The pulse width range (900µs to 2100µs) defines the minimum and maximum positions
  myservo.attach(servoPin, 900, 2100);
  
  delay(2000);        //After this time turn off the power led
  M5.Axp.SetLed(0);

  Serial.println("Servo Control Started");
  
  // Add 10 second (led off + this timer) delay before starting servo movement
  delay(8000);
}

void loop() {
  // First sweep: from 176 to 2 degrees (moving backward)
  // Note: Replace 176 and 45 with the actual range limits of your servo as indicated on the white label
  for(int pos = 176; pos >= 45; pos--) {
    myservo.write(pos);  // Set the servo position
    delay(1);  // Small delay to control the speed of the sweep
  }
  
  delay(300);  // Short pause at the end of the backward sweep. If the phone seems too heavy, add to this timer 200ms. 
  
  // Second sweep: from 45 to 176 degrees (moving forward)
  for(int pos = 45; pos <= 176; pos++) {
    myservo.write(pos);  // Set the servo position
    delay(1);  // Small delay to control the speed of the sweep
  }
  
  // Add 10 second delay before power off
  delay(10000);    //keep it high enough to program the board before turning off
  
  // Power off the Flipper device
  M5.Axp.PowerOff();
}
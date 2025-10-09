/**
 * BatteryMonitor.h
 * 
 * M5Core2 battery monitoring and charging LED control
 * Version: 1.2
 */

#ifndef BATTERY_MONITOR_H
#define BATTERY_MONITOR_H

#include <M5Core2.h>

// Battery states
enum BatteryState {
    BATTERY_IDLE,
    BATTERY_CHARGING,
    BATTERY_CHARGED
};

// Function declarations
void batteryMonitorInit();
void batteryMonitorUpdate();
BatteryState getBatteryState();
bool isCharging();
bool isFullyCharged();
void updateChargingLED();
void disableLED();
void enableLED(bool blinking = false);

#endif // BATTERY_MONITOR_H 
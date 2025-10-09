/**
 * BatteryMonitor.cpp
 * 
 * Implementation of M5Core2 battery monitoring and charging LED control
 * Version: 1.2
 */

#include "BatteryMonitor.h"

// Constants
#define CHARGING_THRESHOLD_CURRENT 0.05f  // Charging current threshold in A
#define CHARGED_VOLTAGE_THRESHOLD 4.2f    // Fully charged battery voltage threshold
#define LED_BLINK_INTERVAL 1000           // LED blink interval in ms

// Global variables
static BatteryState currentBatteryState = BATTERY_IDLE;
static unsigned long lastLEDToggleTime = 0;
static bool ledState = false;

/**
 * Initialize battery monitoring
 */
void batteryMonitorInit() {
    // Initial LED state - off
    M5.Axp.SetLed(0);
    
    // Set up battery management
    M5.Axp.SetChargeVoltage(0);    // 0 = 4.2V charge voltage
    M5.Axp.SetChargeCurrent(3);    // 3 = 300mA charging current (lower than default)
    
    // Initial battery state
    batteryMonitorUpdate();
}

/**
 * Update battery state
 */
void batteryMonitorUpdate() {
    if (isFullyCharged() && isCharging()) {
        currentBatteryState = BATTERY_CHARGED;
    } 
    else if (isCharging()) {
        currentBatteryState = BATTERY_CHARGING;
    } 
    else {
        currentBatteryState = BATTERY_IDLE;
    }
    
    // Update LED based on current state
    updateChargingLED();
}

/**
 * Get current battery state
 */
BatteryState getBatteryState() {
    return currentBatteryState;
}

/**
 * Check if battery is currently charging
 */
bool isCharging() {
    float chargeCurrent = M5.Axp.GetBatCurrent();
    // Negative current means battery is being charged
    return chargeCurrent < -CHARGING_THRESHOLD_CURRENT;
}

/**
 * Check if battery is fully charged
 */
bool isFullyCharged() {
    float batVoltage = M5.Axp.GetBatVoltage();
    return batVoltage >= CHARGED_VOLTAGE_THRESHOLD;
}

/**
 * Update LED based on battery state
 */
void updateChargingLED() {
    unsigned long currentTime = millis();
    
    switch (currentBatteryState) {
        case BATTERY_CHARGING:
            // Blink LED with 1s interval
            if (currentTime - lastLEDToggleTime >= LED_BLINK_INTERVAL) {
                ledState = !ledState;
                M5.Axp.SetLed(ledState ? 1 : 0);
                lastLEDToggleTime = currentTime;
            }
            break;
            
        case BATTERY_CHARGED:
            // LED continuously on
            if (!ledState) {
                ledState = true;
                M5.Axp.SetLed(1);
            }
            break;
            
        case BATTERY_IDLE:
        default:
            // LED off
            if (ledState) {
                ledState = false;
                M5.Axp.SetLed(0);
            }
            break;
    }
}

/**
 * Disable LED
 */
void disableLED() {
    ledState = false;
    M5.Axp.SetLed(0);
}

/**
 * Enable LED, either steady or blinking
 */
void enableLED(bool blinking) {
    if (blinking) {
        // Start in ON state, will toggle in next update
        ledState = true;
        M5.Axp.SetLed(1);
        lastLEDToggleTime = millis();
    } else {
        // Steady ON
        ledState = true;
        M5.Axp.SetLed(1);
    }
} 
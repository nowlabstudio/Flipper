# M5Stack Battery Monitoring System - Version 1.2

This project implements an optimized audio inference system for M5Core2 with added battery monitoring and charging LED functionality.

## New Features in Version 1.2

### Battery Monitoring
- Continuously monitors battery voltage and charging current
- Detects charging state using the AXP192 power management chip
- Determines when battery is fully charged

### Charging LED Feedback
- When charging: Main LED blinks with 1-second interval
- When fully charged but still connected: LED stays continuously on
- When not charging: LED is off

### Inference Control
- Automatically disables inference processing while charging
- Resumes inference when disconnected from charger
- Reduces power consumption during charging

## Implementation Details

### Files
- **BatteryMonitor.h**: Defines the interface for battery monitoring
- **BatteryMonitor.cpp**: Implements battery state detection and LED control
- **EI_stack_optimized_servo_charging_led.ino**: Main application with battery monitoring integration

### Battery States
- **BATTERY_IDLE**: Not charging (running on battery)
- **BATTERY_CHARGING**: Currently charging
- **BATTERY_CHARGED**: Fully charged while still connected

### Technical Specifications
- Uses AXP192 power management functions to detect charging state
- Charging is detected by monitoring battery current
- Full charge is determined by battery voltage threshold (4.2V)
- LED is controlled using M5.Axp.SetLed() function

## Usage

Simply connect the M5Core2 to a USB power source and the system will:
1. Detect charging state automatically
2. Control LED based on charging state
3. Disable inference while charging to save power
4. Display battery information in serial output

## Notice
While charging, the system will print battery statistics every 5 seconds to the serial monitor. 
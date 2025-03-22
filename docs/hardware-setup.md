# Hardware Setup Guide

## Required Components

1. **Main Controller**
   - M5Core2 ESP32 development board
   - Alternative: Any ESP32 board with sufficient GPIO pins

2. **Audio Input**
   - PDM MEMS microphone (SPM1423 or equivalent)
   - Compatible with I2S interface

3. **Servo Motor**
   - Standard servo motor (tested with SG90)
   - 4.8-6V operating voltage

4. **Power Supply**
   - USB power source (5V, 1A minimum)
   - Optional: LiPo battery for M5Core2

5. **Additional Components**
   - Jumper wires
   - Breadboard or custom PCB
   - Optional: 3D printed enclosure

## Connection Diagram

```
┌───────────────────┐           ┌───────────────────┐
│                   │           │                   │
│      M5Core2      │           │   PDM Microphone  │
│     (ESP32)       │           │                   │
│                   │           │  VCC ┌────────────┼── 3.3V
│  GPIO12 ┌─────────┼───────────┤  CLK │            │
│  GPIO0  ┌─────────┼───────────┤  WS  │            │
│  GPIO34 ┌─────────┼───────────┤  DATA│            │
│  GND    ┌─────────┼───────────┤  GND │            │
│                   │           │      │            │
└───────────────────┘           └──────┼────────────┘
                                       │
┌───────────────────┐                  │
│                   │                  │
│    Servo Motor    │                  │
│                   │                  │
│  Signal ┌─────────┼─── GPIO33        │
│  VCC    ┌─────────┼─── 5V            │
│  GND    ┌─────────┼─── GND           │
│                   │                  │
└───────────────────┘                  │
```

## Detailed Connections

### PDM Microphone

| Microphone Pin | ESP32 Pin | Description              |
|----------------|-----------|--------------------------|
| VCC            | 3.3V      | Power supply             |
| GND            | GND       | Ground                   |
| CLK            | GPIO12    | I2S BCK (Bit Clock)      |
| WS             | GPIO0     | I2S LRCK (Word Select)   |
| DATA           | GPIO34    | I2S DATA (Data Input)    |

### Servo Motor

| Servo Pin      | ESP32 Pin | Description              |
|----------------|-----------|--------------------------|
| Signal (Orange)| GPIO33    | PWM control signal       |
| VCC (Red)      | 5V        | Power supply             |
| GND (Brown)    | GND       | Ground                   |

**Note**: The servo may draw significant current during operation. If using USB power, ensure it can provide at least 1A current. If experiencing brownouts during servo operation, consider using a separate power supply for the servo.

## M5Core2 Specific Setup

If using M5Core2:

1. **Battery Connection**
   - Insert the LiPo battery into the battery connector at the back
   - Ensure proper orientation (red wire to positive terminal)

2. **Power Button**
   - Press the power button on the left side to turn on
   - Hold for 6 seconds to power off

3. **USB-C Connection**
   - Connect USB-C cable for programming and charging
   - The code configures fast charging at 1000mA

## Hardware Considerations

### Microphone Placement

For optimal audio detection:
- Place the microphone away from noise sources
- Avoid covering or obstructing the microphone
- Mount securely to prevent vibration-induced noise
- Consider acoustic insulation for noisy environments

### Servo Mounting

For reliable operation:
- Secure the servo firmly to prevent movement during operation
- Ensure full range of motion (45° to 176°) is unobstructed
- Use appropriate servo horn for your application
- Consider mechanical advantages for improved torque

### Power Management

- USB power is recommended during development
- Battery life will vary based on:
  - Servo activation frequency
  - CPU load
  - Sleep mode implementation
  - Battery capacity

## Hardware Variants

### Alternative Microphones

This project supports other microphone options with minimal code changes:

| Microphone Type | Required Code Changes                         |
|-----------------|----------------------------------------------|
| Analog Mic      | Replace I2S with ADC code, remove PDM mode   |
| I2S (non-PDM)   | Remove PDM mode from I2S configuration       |
| USB Mic         | Complete rewrite of audio capture section    |

### Alternative Servo Motors

Different servo models can be used with adjusted parameters:

| Servo Type      | Required Code Changes                         |
|-----------------|----------------------------------------------|
| Digital Servo   | Adjust PWM frequency in servoInit()          |
| High-Torque     | May require external power supply            |
| Continuous      | Modify servo() function for rotation control |

## Hardware Troubleshooting

### No Microphone Input

1. Check power connections (3.3V and GND)
2. Verify I2S pin connections match code configuration
3. Test microphone with multimeter for proper voltage
4. Try alternative microphone if available

### Servo Not Moving

1. Check signal connection to GPIO33
2. Verify power connection (5V required)
3. Test manually with a simple servo test sketch
4. Check for brownouts during operation (insufficient power)

### System Crashes During Operation

1. Check USB power supply capacity (minimum 1A recommended)
2. Verify stable 3.3V supply during operation
3. Add decoupling capacitors if experiencing noise issues
4. Isolate servo power from microcontroller power if possible

## PCB Design Recommendations

For production deployment, consider:

1. **Power Regulation**
   - Separate regulators for digital and servo circuits
   - Adequate decoupling capacitors
   - Reverse polarity protection

2. **Noise Isolation**
   - Separate ground planes for analog and digital sections
   - Proper microphone placement away from noise sources
   - Ground plane under microphone for shielding

3. **Physical Layout**
   - Keep I2S traces short and equal length
   - Maintain appropriate clearance for servo connections
   - Consider thermal management for continuous operation

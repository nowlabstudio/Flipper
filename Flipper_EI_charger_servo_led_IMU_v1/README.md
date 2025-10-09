# ESP32 Audio Inference System with Motion Detection and Servo Control

## Project Description
This project implements a microphone-based inference system with motion detection capabilities using Edge Impulse on ESP32 with FreeRTOS. The system captures audio via I2S, performs inference using a pre-trained Edge Impulse model, and controls a servo motor based on detection results. It also includes a sophisticated motion detection system that monitors for movement and manages power states for optimal battery life.

## Key Features
- Audio capture using I2S microphone
- Edge Impulse ML inference for audio classification
- Memory optimization with quantized filterbank (~10KB RAM savings)
- Robust thread-safe buffer handling with semaphores
- Non-blocking servo control in separate FreeRTOS task
- Accelerometer-based motion detection via the MPU6886 IMU
- Intelligent power management with three distinct states
- Proper shutdown implementation
- M5Core2 integration with battery management
- RTC-based time tracking for accurate power state management

## Technical Implementation
- Uses FreeRTOS tasks for concurrent audio capture, motion detection, and servo control
- Thread synchronization via semaphores and queues
- Memory-efficient audio processing pipeline
- Configurable detection threshold (audio detection: 0.45, motion detection: 0.15g)
- Multi-core operation with optimal task distribution:
  - Core 0: Audio inference and servo control
  - Core 1: Motion detection and power management
- Well-structured logging with consistent message formatting by category
- Robust error handling and resource cleanup

## Motion Detection System
- Runs as a dedicated task on the second core (Core 1)
- Continuously samples accelerometer data at different rates based on system state
- Calculates deltas between consecutive samples on all three axes
- Compares deltas against a configurable threshold (default: 0.15g)
- Implements three system states:
  - ACTIVE: Full operation with servo enabled, CPU at 240MHz
  - SLEEP: Light sleep state with reduced CPU frequency (80MHz)
  - DEEP_SLEEP: Complete system shutdown with only power button wake-up
- Uses RTC for accurate timing of inactivity periods
- Automatically transitions between states based on configurable timeouts:
  - Light sleep after 10 minutes (600 seconds) of inactivity
  - Deep sleep after 30 minutes (1800 seconds) in sleep state

## Audio Inference System
- Samples audio at 16kHz via I2S microphone
- Edge Impulse model processes audio in ~1.25s chunks
- Audio processing pattern creates a distinctive power profile:
  - ~1.0s for audio sampling (lower power consumption)
  - ~1.25s for DSP and classification (higher power consumption)
- Classification results sent to serial with standardized output format
- Triggers servo movement when detection confidence exceeds 0.45

## Hardware Requirements
- ESP32 (specifically M5Core2)
- I2S microphone
- MPU6886 IMU (built into M5Core2)
- Servo motor (connected to pin 33)
- Battery (managed by M5Core2 AXP system)

## Dependencies
- Edge Impulse SDK (with custom model: Flipcase_v1_inferencing.h)
- ESP32Servo
- ESP32PWM
- M5Core2 library
- FreeRTOS

## Configuration Parameters
All system parameters are centralized in the `MotionDefaults` namespace and can be modified at runtime:
- Motion threshold: 0.15g (adjustable via setThreshold())
- Light sleep timeout: 600 seconds (10 minutes) (adjustable via setLightSleepTimeout())
- Deep sleep timeout: 1800 seconds (30 minutes) (adjustable via setDeepSleepTimeout())
- Sampling rates: 10Hz in active mode, 1Hz in sleep mode
- Wake delay: 500ms

## Design Considerations
- Prioritizes memory efficiency on resource-constrained ESP32
- Uses proper multi-threading patterns for responsive operation
- Implements clean resource management and power-saving modes
- Provides diagnostic messaging for debugging with clear categorization
- Uses singleton pattern for global access to the motion manager
- Implements proper shutdown handling for both subsystems
- Consistent interface for configuration and state management

## System Architecture
- **Audio Inference**: Captures and processes audio data, performs ML inference
- **Servo Control**: Manages servo movements based on detection results
- **MotionManager**: Core component that manages motion detection and state transitions
- **Power Management**: Handles transitions between power states based on activity

## Next Steps
- Implement onboard LED feedback
- Improve model accuracy or explore different model architectures
- Add Wi-Fi connectivity for remote monitoring
- Further optimize power consumption for extended battery life
# ESP32 Audio Inference System with Servo Control

## Overview

This project implements a real-time audio inference system using Edge Impulse on an ESP32 with M5Core2 integration. The system listens for specific audio patterns using a microphone, runs inference through a trained machine learning model, and controls a servo motor based on detection results.

Key features:
- Real-time audio processing with optimized memory usage
- FreeRTOS task-based architecture for concurrent operations
- Thread-safe buffer handling with semaphores and queues
- Power management with USB charging control
- Non-blocking servo control via dedicated task

## Hardware Requirements

- ESP32 development board (M5Core2)
- PDM microphone (connected via I2S)
- Servo motor
- USB power source for charging

## Dependencies

- Edge Impulse SDK (Flipcase_v1.2_inferencing.h)
- FreeRTOS
- ESP32Servo
- ESP32PWM
- M5Core2

## System Architecture

### Audio Processing Pipeline

The system implements a complete audio processing pipeline:
1. **Capture**: PDM microphone data is captured via I2S interface
2. **Buffering**: Audio samples are stored in a thread-safe buffer
3. **Inference**: Edge Impulse model processes audio to detect patterns
4. **Action**: Based on inference results, servo motor is activated

### Task Structure

The application uses a multi-task approach to ensure real-time performance:
- **Audio Capture Task**: High-priority task for continuous audio sampling
- **Servo Control Task**: Separate task for non-blocking servo operations
- **Main Loop**: Handles inference processing and decision logic

### Thread Synchronization

Multiple synchronization primitives ensure thread safety:
- **Mutex Semaphore**: Protects shared audio buffer access
- **Command Queue**: Thread-safe communication for servo control

## Memory Optimization

The system includes several memory optimization techniques:
- **Quantized Filterbank**: Saves approximately 10KB RAM
- **Optimized Buffer Sizes**: Carefully tuned for the application
- **Task Stack Sizes**: Appropriately sized to minimize memory usage

## Power Management

The application implements battery management:
- Configurable charging current (set to 1000mA)
- Automatic switching between USB and battery power
- LED control for power status indication

## Installation and Setup

1. Install required libraries via Arduino Library Manager:
   - ESP32Servo
   - ESP32PWM
   - M5Core2

2. Set up Edge Impulse:
   - Train a model for your specific audio detection needs
   - Export as Arduino library and include in your project
   - Replace the header file reference with your model name

3. Configure pins according to your hardware setup:
   - Update I2S pins if different from default configuration
   - Set the correct servo pin

## Usage

The system starts automatically upon power-up and:
1. Initializes the microphone and servo
2. Begins continuous audio capture
3. Runs inference on captured audio
4. Activates the servo when audio pattern is detected with confidence > 0.45

## Customization

### Detection Sensitivity

Adjust detection threshold in the main loop:
```cpp
if (highest_index == 0 && highest_value > 0.45) {  // Adjust threshold as needed
    // Trigger servo
}
```

### Servo Movement Pattern

Modify the servo movement pattern in servo.cpp:
```cpp
void servo(int delayTime) {
    // Customize movement pattern here
}
```

### Audio Amplification

Adjust the audio amplification factor:
```cpp
sampleBuffer[x] = (int16_t)(sampleBuffer[x]) * 10;  // Change amplification factor
```

## Advanced Configuration

### I2S Configuration

The I2S interface is configured for PDM microphone input:
```cpp
i2s_config_t i2s_config = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX | I2S_MODE_PDM),
    .sample_rate = 16000,  // 16kHz for speech recognition
    // ... other settings
};
```

### Memory Allocation

The system dynamically allocates memory for audio processing:
```cpp
inference.buffer = (int16_t *)malloc(n_samples * sizeof(int16_t));
```

## Troubleshooting

### Common Issues

1. **Memory Allocation Failures**:
   - Reduce the `EI_CLASSIFIER_RAW_SAMPLE_COUNT` value
   - Enable quantized filterbank with `#define EIDSP_QUANTIZE_FILTERBANK 1`

2. **I2S Configuration Errors**:
   - Verify pin connections match configuration
   - Check that PDM microphone is properly connected

3. **Low Detection Accuracy**:
   - Adjust audio amplification factor
   - Retrain model with more diverse samples

## Contributing

Contributions to this project are welcome. Please follow these steps:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

[Specify your license here]

## Credits

- Edge Impulse for the machine learning framework
- ESP32 and FreeRTOS communities
- M5Stack for the M5Core2 platform

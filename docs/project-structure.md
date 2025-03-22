# Project Structure Documentation

## Directory Structure

```
ESP32_Audio_Inference_System/
├── src/
│   ├── EI_stack_optimized_servo_charging_led.ino    # Main application file
│   ├── servo.cpp                                    # Servo control implementation
│   └── include/                                     # Header files
├── lib/                                             # Dependencies
│   ├── Edge_Impulse/                                # Generated model library
│   │   └── Flipcase_v1.2_inferencing/               # Model-specific files
│   └── README.md                                    # Libraries documentation
├── docs/                                            # Additional documentation
│   ├── hardware_setup.md                            # Hardware connection guide
│   ├── model_training.md                            # Model training instructions
│   └── imgs/                                        # Documentation images
├── .gitignore                                       # Git ignore file
├── LICENSE                                          # License file
└── README.md                                        # Project overview
```

## Key Components

### Main Application (EI_stack_optimized_servo_charging_led.ino)

The main application file implements:
- FreeRTOS task management
- Audio capture via I2S
- Edge Impulse inference
- Semaphore-based buffer protection
- Power management
- Command queue for servo control

### Servo Control (servo.cpp)

Dedicated module for servo operations:
- Servo initialization
- Movement patterns implementation
- Timing control

### Edge Impulse Model

The machine learning model (Flipcase_v1.2_inferencing) is trained to recognize specific audio patterns. The model is integrated as a library and processes audio data to make predictions.

## Task Architecture

```
┌────────────────────┐      ┌────────────────────┐
│   Main Application │      │    Audio Capture   │
│   ----------------─┼─────▶│    -------------   │
│   - Inference      │      │    - I2S Reading   │
│   - Decision Logic │      │    - Buffer Update │
└─────────┬──────────┘      └────────────────────┘
          │                              ▲
          │                              │
          │                              │
          │                     ┌────────┴─────────┐
          │                     │  Buffer (shared) │
          │                     └──────────────────┘
          │
          ▼
┌────────────────────┐
│   Servo Control    │
│   -------------    │
│   - Command Queue  │
│   - Motor Control  │
└────────────────────┘
```

## Memory Management

The application optimizes memory usage:

| Component               | Memory Usage   | Optimization                    |
|-------------------------|----------------|----------------------------------|
| Audio Buffer            | ~4KB           | Quantized filterbank             |
| Inference Buffer        | ~32KB          | Dynamic allocation               |
| Audio Capture Task      | 16KB stack     | Reduced from default 32KB        |
| Servo Task              | 4KB stack      | Minimal stack allocation         |
| I2S DMA Buffers         | ~2KB           | Optimized buffer count/length    |

## Synchronization Mechanisms

| Mechanism       | Type      | Purpose                                   |
|-----------------|-----------|-------------------------------------------|
| buffer_semaphore| Mutex     | Protects shared audio buffer access       |
| servoCommandQueue| Queue    | Enables non-blocking servo control        |

## I2S Configuration

The I2S interface is configured for audio capture:

| Parameter             | Value                       | Purpose                      |
|-----------------------|-----------------------------|------------------------------|
| Mode                  | MASTER, RX, PDM             | PDM microphone support       |
| Sample Rate           | 16kHz                       | Optimized for speech         |
| Bits Per Sample       | 16-bit                      | Standard audio precision     |
| Channel Format        | Right channel only          | Single channel capture       |
| DMA Buffer Count      | 2                           | Minimizes memory usage       |
| DMA Buffer Length     | 512                         | Balances latency/memory      |

## Error Handling

The application implements robust error handling:
- I2S driver installation checks
- Memory allocation verification
- Timeout handling for buffer operations
- Task creation failure detection
- Proper resource cleanup on errors

## Safety Features

- Timeout protection to prevent deadlocks
- Resource cleanup on shutdown
- Proper task deletion sequence
- Battery management with automatic switching

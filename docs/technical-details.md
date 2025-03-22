# Technical Details and Implementation Notes

## Audio Inference Implementation

### Signal Processing Pipeline

The audio processing pipeline consists of several stages:

1. **PDM Microphone Capture**
   - PDM (Pulse Density Modulation) data is captured via I2S interface
   - Configured for 16kHz sampling rate, optimal for speech recognition
   - 16-bit depth provides adequate resolution for inference

2. **Buffer Management**
   - Double-buffering approach with DMA
   - Buffer size: 2048 samples (128ms @16kHz)
   - Thread-safe access via semaphore protection

3. **Signal Preprocessing**
   - Amplification: Raw samples are amplified by a factor of 10
   - No additional filtering is performed as Edge Impulse handles this internally

4. **Feature Extraction**
   - Handled by Edge Impulse DSP pipeline
   - Includes spectral analysis (MFCCs or spectrograms)
   - Quantized filterbank saves approximately 10KB of RAM

5. **Classification**
   - Neural network inference via Edge Impulse SDK
   - Model quantized for optimal performance on ESP32
   - Classification results include confidence scores for each class

### FreeRTOS Implementation Details

#### Task Priorities and Stack Sizes

| Task             | Priority | Stack (KB) | Responsibility                                |
|------------------|----------|------------|-----------------------------------------------|
| Audio Capture    | 10       | 16         | Time-critical I2S data collection             |
| Servo Control    | 5        | 4          | Non-time-critical servo motor operations      |
| Main Loop        | Default  | Default    | Inference processing and decision making      |

#### CPU Core Assignment

Tasks are not explicitly pinned to specific cores, allowing FreeRTOS scheduler to optimize core usage based on workload.

#### Critical Sections

Critical sections are managed using mutex semaphores rather than disabling interrupts to maintain system responsiveness.

### Memory Usage Breakdown

| Component                   | RAM Usage     | Flash Usage    |
|-----------------------------|---------------|----------------|
| Edge Impulse Runtime        | ~30KB         | ~100KB         |
| Audio Buffers               | ~8KB          | -              |
| I2S DMA Buffers             | ~2KB          | -              |
| Task Stacks                 | ~24KB         | -              |
| Application Code            | ~2KB          | ~60KB          |
| M5Core2 Framework           | ~20KB         | ~150KB         |
| FreeRTOS                    | ~8KB          | ~50KB          |
| **Total**                   | **~94KB**     | **~360KB**     |

## Servo Control Implementation

### Technical Specifications

- Operating frequency: 333Hz (configurable via `setPeriodHertz()`)
- Pulse width range: 900µs to 2100µs
- Angular range: 45° to 176° (limited for mechanical constraints)
- Control pin: GPIO 33

### Movement Pattern

The servo implementation follows a specific movement pattern:
1. **Backward Motion**: 176° → 45° at 1ms intervals (smooth motion)
2. **Brief Pause**: 300ms delay
3. **Forward Motion**: 45° → 176° at maximum speed (no delay between positions)
4. **Wait Period**: Configurable delay before next activation

### Command Queue Implementation

Commands to the servo task are sent via a FreeRTOS queue with the following structure:

```cpp
typedef struct {
    bool activate;   // Whether to activate the servo
    int delayTime;   // Delay parameter for the servo movement
} ServoCommand_t;
```

This allows for non-blocking servo operation with configurable parameters.

## Power Management

### Battery Charging Configuration

M5Core2's AXP192 power management IC is configured with:
- Bus power mode: 0 (automatic USB/battery switching)
- Charging current: 11 (corresponds to 1000mA)
- LED indicator disabled to save power

### Power Consumption

Estimated power consumption in different states:

| State                           | Current Draw  | Notes                           |
|---------------------------------|---------------|----------------------------------|
| Idle (listening)                | ~80mA         | Primary power consumption state  |
| Active inference                | ~120mA        | Brief peaks during processing    |
| Servo activation                | ~200mA        | Short duration current spikes    |
| Deep sleep (not implemented)    | ~10mA         | Could be added for battery saving|

## I2S Implementation Details

### Pin Configuration

| Function   | GPIO Pin |
|------------|----------|
| BCK        | 12       |
| LRCK/WS    | 0        |
| DATA OUT   | 2        |
| DATA IN    | 34       |

### PDM Configuration

PDM (Pulse Density Modulation) microphones require specific I2S configuration:
- Special PDM mode enabled
- Single channel (right-only)
- Standard I2S communication format
- ESP32's built-in decimation filter used

### Error Handling

I2S driver implementation includes comprehensive error handling:
- Driver installation verification
- Pin configuration validation
- Read operation timeout detection
- Partial read handling
- Proper driver uninstallation on shutdown

## Edge Impulse Integration

### Model Configuration

- Sample length: Variable based on model configuration
- Frame size: Determined by Edge Impulse export
- Inference interval: Continuous processing
- Classification outputs: Multiple classes with confidence scores

### Performance Metrics

Expected performance metrics (may vary based on exact model):
- DSP processing time: ~15-30ms
- Classification time: ~10-25ms
- Anomaly detection (if enabled): ~5-10ms
- Total inference latency: ~30-65ms

## Troubleshooting and Debugging

### Debug Outputs

The code includes extensive debug outputs via serial:
- Inference results with confidence scores
- Timing information for DSP and classification
- Error messages for critical failures
- Status updates for servo movements

### Common Issues

1. **High Memory Usage**
   - Solution: Enable quantized filterbank with `#define EIDSP_QUANTIZE_FILTERBANK 1`
   - Solution: Reduce the model complexity or sample length

2. **I2S Communication Issues**
   - Check: Verify pin connections match configuration
   - Check: Ensure PDM microphone is compatible with ESP32

3. **Servo Jitter**
   - Cause: Power supply fluctuations
   - Solution: Provide separate power source for servo

4. **False Detections**
   - Solution: Adjust confidence threshold (currently 0.45)
   - Solution: Retrain model with more diverse negative samples

## Future Improvements

1. **Power Optimization**
   - Implement deep sleep during inactive periods
   - Reduce inference frequency when no activity detected

2. **Enhanced Error Recovery**
   - Implement watchdog timer for system reset on hang
   - Add periodic buffer integrity checks

3. **Feature Enhancements**
   - WiFi connectivity for remote monitoring
   - SD card logging of detection events
   - Multiple detection response patterns

4. **Code Refactoring**
   - Split functionality into multiple files
   - Create configurable parameters header
   - Implement unit tests for core functionality

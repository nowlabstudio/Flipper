#ifndef MOTION_MANAGER_H
#define MOTION_MANAGER_H

/**
 * Motion Manager - Header File
 * 
 * Defines the interface for the motion detection system.
 * This system uses the MPU6886 IMU to detect movement
 * and manages system state transitions between active
 * and sleep modes.
 * 
 * Enhanced with RTC-based timing and deep sleep functionality:
 * - Uses RTC for accurate timing of inactivity periods
 * - Implements two-level power management:
 *   1. Light sleep after 30 seconds of inactivity (CPU slowdown)
 *   2. Deep sleep after 60 seconds in sleep mode (only power button wake-up)
 */

#include <Arduino.h>

// M5Core2 library that includes the MPU6886 implementation
#include <M5Core2.h>

// For ESP32 deep sleep functionality
#include <esp_sleep.h>

// Default configuration values - accessible from both motion_manager.cpp and main program
namespace MotionDefaults {
    const float MOTION_THRESHOLD = 0.15f;         // Movement threshold in g
    const uint32_t LIGHT_SLEEP_TIMEOUT = 600;     // Light sleep timeout in seconds (10min)600
    const uint32_t DEEP_SLEEP_TIMEOUT = 1800;      // Deep sleep timeout in seconds (30min)1800
    const uint16_t SAMPLE_RATE_ACTIVE = 10;      // Sampling rate in active mode (10Hz)
    const uint16_t SAMPLE_RATE_SLEEP = 1;        // Sampling rate in sleep mode (1Hz)
    const uint16_t WAKE_DELAY = 500;             // Wake delay in milliseconds
}

// System state enumeration
enum SystemState {
  ACTIVE,  // Full operation, servo enabled
  SLEEP,   // Light sleep state, CPU slowed, servo disabled
  DEEP_SLEEP // Deep sleep state, system shutdown until power button press
};

// RTC time structure
struct RTCTime {
  uint8_t hour;
  uint8_t minute; 
  uint8_t second;
};

// Motion detection configuration structure
struct MotionConfig {
  float threshold;              // Movement threshold in g (default: 0.1g)
  uint32_t lightSleepTimeout;   // Light sleep timeout in seconds (default: 60s = 1 minute)
  uint32_t deepSleepTimeout;    // Deep sleep timeout in seconds (default: 600s = 10 minutes)
  uint16_t sampleRateActive;    // Sampling rate in active mode (default: 10Hz)
  uint16_t sampleRateSleep;     // Sampling rate in sleep mode (default: 1Hz)
  uint16_t wakeDelay;           // Wake delay in milliseconds (default: 500ms)
};

// Motion manager class
class MotionManager {
private:
  // MPU6886 is already initialized as part of M5Core2
  SystemState currentState;
  MotionConfig config;
  
  // RTC timing variables
  RTCTime lastMovementRtcTime;
  bool rtcInitialized;
  
  // Legacy millisecond-based timing (backup)
  unsigned long lastMovementTime;
  
  float lastX, lastY, lastZ;
  TaskHandle_t motionTaskHandle;
  
  // FreeRTOS queue handle for state changes
  QueueHandle_t stateQueue;
  
  // Motion detection algorithm
  bool detectMotion();
  
  // Static task function for FreeRTOS
  static void motionTaskCode(void* parameter);
  
  // Task function implementation
  void motionTask();
  
  // RTC timing functions
  void updateLastMovementTime();
  
  // Deep sleep functions
  void enterDeepSleep();

public:
  MotionManager();
  ~MotionManager();
  
  // Initialize with default or custom configuration
  bool begin(MotionConfig* customConfig = nullptr);
  
  // Get current system state
  SystemState getState();
  
  // Check if state change is available
  bool stateChangeAvailable();
  
  // Get new state change (to be called from main core)
  SystemState getStateChange();
  
  // Force state change (for testing/manual override)
  void setState(SystemState newState);
  
  // Power management functions
  void enterSleepMode();
  void exitSleepMode();
  
  // Check if device is waking from deep sleep
  bool isWakingFromDeepSleep();
  
  // Configuration functions
  void setThreshold(float threshold);
  void setLightSleepTimeout(uint32_t timeoutSeconds);
  void setDeepSleepTimeout(uint32_t timeoutSeconds);
  
  // Get inactivity time in seconds
  uint32_t getInactivitySeconds();
};

// Global function to access motion manager from other files
MotionManager& getMotionManager();

#endif // MOTION_MANAGER_H
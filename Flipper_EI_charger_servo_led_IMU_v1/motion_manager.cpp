/*
 * Motion Manager Implementation
 * 
 * This file implements the motion detection system using the MPU6886 IMU.
 * Key features:
 * - Runs as a dedicated task on the second core (Core 1)
 * - Monitors accelerometer data to detect movement
 * - Controls system state changes (ACTIVE/SLEEP/DEEP_SLEEP)
 * - Implements power management with light sleep and deep sleep modes
 * - Uses a singleton pattern for global access
 * - Uses RTC for accurate inactivity timing
 * 
 * The motion detection algorithm:
 * - Samples accelerometer data at configurable rates
 * - Calculates deltas between consecutive samples
 * - Compares deltas to a configurable threshold
 * - Determines movement when any axis exceeds the threshold
 * 
 * Power management:
 * - In SLEEP mode, reduces CPU frequency to save power
 * - In DEEP_SLEEP mode, uses ESP32 deep sleep for maximum power saving
 * - Automatic transitions based on configurable timeouts
 */

#include "motion_manager.h"

// Define a key to identify wakeup cause in RTC memory
#define DEEP_SLEEP_WAKEUP_KEY 0x4D415252  // "MARR" in hex

// RTC data that persists during deep sleep
RTC_DATA_ATTR static uint32_t wakeupCause = 0;

// Singleton instance
static MotionManager* _instance = nullptr;

// Global access function
MotionManager& getMotionManager() {
  if (!_instance) {
    _instance = new MotionManager();
  }
  return *_instance;
}

// Constructor
MotionManager::MotionManager() : 
  currentState(ACTIVE), 
  rtcInitialized(false),
  lastMovementTime(0),
  lastX(0), lastY(0), lastZ(0),
  motionTaskHandle(nullptr) {
  
  // Initialize RTC time struct
  lastMovementRtcTime = {0, 0, 0};
  
  // Default configuration - using values from the namespace
  config.threshold = MotionDefaults::MOTION_THRESHOLD;
  config.lightSleepTimeout = MotionDefaults::LIGHT_SLEEP_TIMEOUT;
  config.deepSleepTimeout = MotionDefaults::DEEP_SLEEP_TIMEOUT;
  config.sampleRateActive = MotionDefaults::SAMPLE_RATE_ACTIVE;
  config.sampleRateSleep = MotionDefaults::SAMPLE_RATE_SLEEP;
  config.wakeDelay = MotionDefaults::WAKE_DELAY;
  
  // Create state change queue
  stateQueue = xQueueCreate(5, sizeof(SystemState));
  
  // Record wakeup cause if coming from deep sleep
  if (esp_sleep_get_wakeup_cause() != ESP_SLEEP_WAKEUP_UNDEFINED) {
    wakeupCause = DEEP_SLEEP_WAKEUP_KEY;
  }
}

// Destructor
MotionManager::~MotionManager() {
  if (motionTaskHandle) {
    vTaskDelete(motionTaskHandle);
  }
  
  if (stateQueue) {
    vQueueDelete(stateQueue);
  }
  
  if (_instance == this) {
    _instance = nullptr;
  }
}

// Initialize motion manager
bool MotionManager::begin(MotionConfig* customConfig) {
  // Apply custom configuration if provided
  if (customConfig) {
    config = *customConfig;
  }
  
  // The M5Core2 already initialized the IMU
  // Try to read data, if unsuccessful, then it wasn't initialized
  float testX, testY, testZ;
  M5.IMU.getAccelData(&testX, &testY, &testZ);
  if (testX == 0 && testY == 0 && testZ == 0) {
    Serial.println("IMU initialization failed or not responsive");
    return false;
  }
  Serial.println("IMU initialized successfully");
  
  // Store initial acceleration values
  M5.IMU.getAccelData(&lastX, &lastY, &lastZ);
  
  // M5Core2 RTC is automatically initialized by M5.begin()
  // Just mark RTC as initialized and start using it
  rtcInitialized = true;
  
  // Initialize RTC timestamp
  updateLastMovementTime();
  Serial.println("RTC initialized successfully");
  
  // Create motion detection task on core 1 (second core)
  BaseType_t result = xTaskCreatePinnedToCore(
    motionTaskCode,        // Task function
    "MotionTask",          // Task name
    4096,                  // Stack size
    this,                  // Task parameter (this instance)
    1,                     // Priority (lower than audio processing)
    &motionTaskHandle,     // Task handle
    1                      // Run on core 1 (second core)
  );
  
  return result == pdPASS;
}

// Check if device is waking from deep sleep
bool MotionManager::isWakingFromDeepSleep() {
  return wakeupCause == DEEP_SLEEP_WAKEUP_KEY;
}

// Update the last movement time from RTC
void MotionManager::updateLastMovementTime() {
  if (rtcInitialized) {
    RTC_TimeTypeDef timeStruct;
    M5.Rtc.GetTime(&timeStruct);
    
    lastMovementRtcTime.hour = timeStruct.Hours;
    lastMovementRtcTime.minute = timeStruct.Minutes;
    lastMovementRtcTime.second = timeStruct.Seconds;
    
    Serial.print("Movement time updated: ");
    Serial.print(lastMovementRtcTime.hour);
    Serial.print(":");
    Serial.print(lastMovementRtcTime.minute);
    Serial.print(":");
    Serial.println(lastMovementRtcTime.second);
  } else {
    // Fallback to millis() if RTC is not available
    lastMovementTime = millis();
  }
}

// Calculate seconds of inactivity
uint32_t MotionManager::getInactivitySeconds() {
  if (rtcInitialized) {
    RTC_TimeTypeDef currentTime;
    M5.Rtc.GetTime(&currentTime);
    
    // Calculate total seconds for both times
    uint32_t lastTimeSeconds = (lastMovementRtcTime.hour * 3600) + 
                              (lastMovementRtcTime.minute * 60) + 
                               lastMovementRtcTime.second;
    
    uint32_t currentTimeSeconds = (currentTime.Hours * 3600) + 
                                 (currentTime.Minutes * 60) + 
                                  currentTime.Seconds;
    
    // Calculate difference, handling day wraparound
    uint32_t diffSeconds;
    if (currentTimeSeconds >= lastTimeSeconds) {
      diffSeconds = currentTimeSeconds - lastTimeSeconds;
    } else {
      // Handle day wraparound (24 hours = 86400 seconds)
      diffSeconds = (86400 - lastTimeSeconds) + currentTimeSeconds;
    }
    
    return diffSeconds;
  } else {
    // Fallback to millis() if RTC is not available
    return (millis() - lastMovementTime) / 1000;
  }
}

// Static task function entry point
void MotionManager::motionTaskCode(void* parameter) {
  MotionManager* self = static_cast<MotionManager*>(parameter);
  self->motionTask();
}

// Motion detection task implementation
void MotionManager::motionTask() {
  TickType_t xLastWakeTime;
  const TickType_t xActiveFrequency = 1000 / config.sampleRateActive;  // Active mode frequency
  const TickType_t xSleepFrequency = 1000 / config.sampleRateSleep;    // Sleep mode frequency
  
  xLastWakeTime = xTaskGetTickCount();
  
  while (true) {
    TickType_t frequency = (currentState == ACTIVE) ? xActiveFrequency : xSleepFrequency;
    
    // Check for motion
    if (detectMotion()) {
      // Update last movement time using RTC if available
      updateLastMovementTime();
      
      // If we're in SLEEP state, transition to ACTIVE
      if (currentState == SLEEP) {
        Serial.println("\n*** MOTION DETECTED - WAKING UP ***");
        exitSleepMode();
        currentState = ACTIVE;
        
        // Notify main core about state change
        SystemState newState = ACTIVE;
        xQueueSend(stateQueue, &newState, 0);
        Serial.println("State change: SLEEP -> ACTIVE\n");
      }
    } else {
      // Get inactivity time in seconds using RTC or millis backup
      uint32_t inactivitySeconds = getInactivitySeconds();
      
      // Check if light sleep timeout has elapsed
      if (currentState == ACTIVE && inactivitySeconds >= config.lightSleepTimeout) {
        // Transition to SLEEP state
        Serial.println("\n*** ENTERING SLEEP MODE ***");
        Serial.println("Timeout: " + String(config.lightSleepTimeout) + " seconds of inactivity");
        
        enterSleepMode();
        currentState = SLEEP;
        
        // Notify main core about state change
        SystemState newState = SLEEP;
        xQueueSend(stateQueue, &newState, 0);
        Serial.println("State change: ACTIVE -> SLEEP\n");
      }
      
      // Check if deep sleep timeout has elapsed
      else if (currentState == SLEEP && inactivitySeconds >= config.deepSleepTimeout) {
        // Transition to DEEP_SLEEP state
        Serial.println("\n*** ENTERING DEEP_SLEEP MODE ***");
        Serial.println("Timeout: " + String(config.deepSleepTimeout) + " seconds in SLEEP state");
        
        // Notify main core about state change before going to deep sleep
        SystemState newState = DEEP_SLEEP;
        xQueueSend(stateQueue, &newState, 0);
        Serial.println("State change: SLEEP -> DEEP_SLEEP\n");
        
        // Delay to allow main core to process the state change
        delay(1000);
        
        // Enter deep sleep
        enterDeepSleep();
        
        // Code should never reach here as deep sleep restarts the device
        currentState = DEEP_SLEEP;
      }
    }
    
    // We've removed detailed debug output here since the main program handles status display
    
    // Delay until next sample
    vTaskDelayUntil(&xLastWakeTime, frequency);
  }
}

// Motion detection algorithm
bool MotionManager::detectMotion() {
  float x, y, z;
  M5.IMU.getAccelData(&x, &y, &z);
  
  // Calculate movement delta
  float deltaX = fabs(x - lastX);
  float deltaY = fabs(y - lastY);
  float deltaZ = fabs(z - lastZ);
  
  // Debug - show motion events when they occur
  static unsigned long lastDebugTime = 0;
  unsigned long currentTime = millis();
  
  // Only output when motion is detected, not regular accelerometer values
  bool motionDetected = (deltaX > config.threshold || deltaY > config.threshold || deltaZ > config.threshold);
  
  if (motionDetected || (currentTime - lastDebugTime > 10000)) { // Every 10 seconds or on motion
    lastDebugTime = currentTime;
    
    if (motionDetected) {
      Serial.println("[MOTION] Movement detected! Threshold: " + String(config.threshold, 2) + "g");
    }
    
    // We don't need to print detailed status here as the main program does this
  }
  
  // Update previous values
  lastX = x;
  lastY = y;
  lastZ = z;
  
  // Check if any axis exceeds the threshold
  return (deltaX > config.threshold || 
          deltaY > config.threshold || 
          deltaZ > config.threshold);
}

// Check if there's a state change in the queue
bool MotionManager::stateChangeAvailable() {
  return uxQueueMessagesWaiting(stateQueue) > 0;
}

// Get state change from queue
SystemState MotionManager::getStateChange() {
  SystemState newState;
  if (xQueueReceive(stateQueue, &newState, 0) == pdTRUE) {
    return newState;
  }
  return currentState;
}

// Get current state
SystemState MotionManager::getState() {
  // Return the actual state
  return currentState;
}

// Force state change
void MotionManager::setState(SystemState newState) {
  if (newState != currentState) {
    if (newState == SLEEP) {
      enterSleepMode();
    } else {
      exitSleepMode();
    }
    currentState = newState;
  }
}

// Enter sleep mode (light sleep - CPU frequency reduction)
void MotionManager::enterSleepMode() {
  // Reduce IMU sampling rate to save power
  // Note: Implementation depends on specific IMU used
  
  // Reduce CPU frequency for power saving
  #ifdef ESP32
  setCpuFrequencyMhz(80); // Reduce from default 240MHz to 80MHz
  Serial.println("CPU frequency reduced to 80MHz for power saving");
  #endif
  
  // Update AXP192 power management settings
  M5.Axp.SetLDO2(false);  // Turn off LDO2 (vibration motor power)
  // M5Core2 doesn't use LDO3, it's only available on M5Stack Gray
  
  // Turn off LCD backlight
  M5.Axp.SetLcdVoltage(2500);
  M5.Axp.SetDCDC3(false);  // Turn off LCD
  
  Serial.println("Power management optimized for sleep mode");
}

// Exit sleep mode
void MotionManager::exitSleepMode() {
  // Restore IMU sampling rate
  
  // ESP32 specific: Restore CPU frequency
  #ifdef ESP32
  setCpuFrequencyMhz(240); // Back to default 240MHz
  #endif
  
  // Restore AXP192 power management settings
  M5.Axp.SetLcdVoltage(3300);
  M5.Axp.SetDCDC3(true);   // Turn on LCD
  
  // Small delay to allow system to stabilize
  delay(config.wakeDelay);
  
  Serial.println("Power management restored for active mode");
}

// Enter deep sleep mode
void MotionManager::enterDeepSleep() {
  Serial.println("Preparing for deep sleep...");
  
  // Flush serial before sleep
  Serial.flush();
  
  // Configure deep sleep wake sources
  esp_sleep_enable_ext0_wakeup(GPIO_NUM_37, 1); // Power button (GPIO37 on M5Core2)
  
  // Store marker in RTC memory to identify deep sleep wake-up
  wakeupCause = DEEP_SLEEP_WAKEUP_KEY;
  
  // Enter deep sleep
  Serial.println("*** DEEP SLEEP ACTIVE - Press POWER button to wake up ***");
  Serial.flush();
  
  // Power down all peripherals
  M5.Axp.PowerOff();
  
  // Enter deep sleep
  esp_deep_sleep_start();
  
  // Code will never reach here
}

// Configuration setters
void MotionManager::setThreshold(float threshold) {
  config.threshold = threshold;
}

void MotionManager::setLightSleepTimeout(uint32_t timeoutSeconds) {
  config.lightSleepTimeout = timeoutSeconds;
  Serial.print("Light sleep timeout set to ");
  Serial.print(timeoutSeconds);
  Serial.println(" seconds");
}

void MotionManager::setDeepSleepTimeout(uint32_t timeoutSeconds) {
  config.deepSleepTimeout = timeoutSeconds;
  Serial.print("Deep sleep timeout set to ");
  Serial.print(timeoutSeconds);
  Serial.println(" seconds");
}
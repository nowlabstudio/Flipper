/**
 * Optimized ESP32 Audio Inference System with Servo Control
 * 
 * This code implements a microphone-based inference system using Edge Impulse
 * on ESP32 with FreeRTOS, with servo control based on inference results.
 * Key optimizations include:
 * - Memory usage optimization with quantized filterbank
 * - Robust buffer handling with semaphores
 * - Proper shutdown implementation
 * - Non-blocking servo control with separate task
 */

// Enable quantized filterbank to save ~10KB RAM
#define EIDSP_QUANTIZE_FILTERBANK   1

#include <Flipcase_v1_inferencing.h>  //v1.0 is the latest tested
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/semphr.h"
#include "freertos/queue.h"
#include "driver/i2s.h"
#include <ESP32Servo.h>
#include <ESP32PWM.h>
#include <M5Core2.h>

// Pin definitions for I2S interface
#define CONFIG_I2S_BCK_PIN     12
#define CONFIG_I2S_LRCK_PIN    0
#define CONFIG_I2S_DATA_PIN    2
#define CONFIG_I2S_DATA_IN_PIN 34
#define Speak_I2S_NUMBER I2S_NUM_0
#define MODE_MIC  0
#define DATA_SIZE 1024

// Servo-related definitions
extern Servo myservo;
const int servoPin = 33;

// Function prototypes for servo control
void servoInit();
void servo(int delayTime);

// Audio configuration
#define SAMPLE_RATE 16000U
#define SAMPLE_BITS 16

// Task handles
TaskHandle_t captureTaskHandle = NULL;
TaskHandle_t servoTaskHandle = NULL;

// Semaphores and queues for thread synchronization
SemaphoreHandle_t buffer_semaphore = NULL;
QueueHandle_t servoCommandQueue = NULL;

// Servo control command structure
typedef struct {
    bool activate;
    int delayTime;
} ServoCommand_t;

/** Audio buffers, pointers and selectors */
typedef struct {
    int16_t *buffer;
    uint8_t buf_ready;
    uint32_t buf_count;
    uint32_t n_samples;
} inference_t;

static inference_t inference;
static const uint32_t sample_buffer_size = 2048;
static signed short sampleBuffer[sample_buffer_size];
static bool debug_nn = false; // Set this to true to see features generated from raw signal
static volatile bool record_status = true;

// Function prototypes
static bool microphone_inference_start(uint32_t n_samples);
static bool microphone_inference_record(void);
static int microphone_audio_signal_get_data(size_t offset, size_t length, float *out_ptr);
static void microphone_inference_end(void);
static void capture_samples(void* arg);
static void servo_task(void* arg);
static void trigger_servo(int delayTime);

/**
 * Setup function - initializes the system
 */
void setup()
{
    // Initialize serial communication
    Serial.begin(115200);
    M5.begin(false, false, true, true); //LCD, SD, Serial, I2C
    
    // Battery and USB charging configuration
    M5.Axp.SetBusPowerMode(0);        // Automatic switching between USB and battery
    M5.Axp.SetCHGCurrent(11);         // Set charging current to 1000mA
    M5.Axp.SetLed(0);
    // Wait for USB connection if needed
    while (!Serial);
    Serial.println("Edge Impulse Inferencing Demo - Optimized Version with Servo Control");

    // Display inferencing settings
    ei_printf("Inferencing settings:\n");
    ei_printf("\tInterval: ");
    ei_printf_float((float)EI_CLASSIFIER_INTERVAL_MS);
    ei_printf(" ms.\n");
    ei_printf("\tFrame size: %d\n", EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE);
    ei_printf("\tSample length: %d ms.\n", EI_CLASSIFIER_RAW_SAMPLE_COUNT / 16);
    ei_printf("\tNo. of classes: %d\n", sizeof(ei_classifier_inferencing_categories) / sizeof(ei_classifier_inferencing_categories[0]));

    // Initialize servo
    ESP32PWM::allocateTimer(0);
    servoInit();
    ei_printf("Servo initialized\n");
    
    // Create semaphore for buffer protection
    buffer_semaphore = xSemaphoreCreateMutex();
    if (buffer_semaphore == NULL) {
        ei_printf("ERR: Failed to create buffer semaphore\n");
        return;
    }
    
    // Create queue for servo commands
    servoCommandQueue = xQueueCreate(5, sizeof(ServoCommand_t));
    if (servoCommandQueue == NULL) {
        ei_printf("ERR: Failed to create servo command queue\n");
        return;
    }
    
    // Create servo control task
    BaseType_t servo_task_created = xTaskCreate(
        servo_task,
        "ServoControl",
        1024 * 4,  // 4KB stack should be sufficient for servo control
        NULL,
        5,         // Lower priority than audio capture
        &servoTaskHandle
    );
    
    if (servo_task_created != pdPASS) {
        ei_printf("ERR: Failed to create servo control task\n");
        return;
    }
    
    ei_printf("\nStarting continuous inference in 2 seconds...\n");
    ei_sleep(2000);

    // Start the microphone inference system
    if (microphone_inference_start(EI_CLASSIFIER_RAW_SAMPLE_COUNT) == false) {
        ei_printf("ERR: Could not allocate audio buffer (size %d), this could be due to the window length of your model\r\n", 
                 EI_CLASSIFIER_RAW_SAMPLE_COUNT);
        return;
    }

    ei_printf("Recording...\n");
}

/**
 * Main loop function - runs inference continuously
 */
void loop()
{
    // Record audio from microphone
    bool m = microphone_inference_record();
    if (!m) {
        ei_printf("ERR: Failed to record audio...\n");
        return;
    }

    // Set up signal for classifier
    signal_t signal;
    signal.total_length = EI_CLASSIFIER_RAW_SAMPLE_COUNT;
    signal.get_data = &microphone_audio_signal_get_data;
    ei_impulse_result_t result = { 0 };

    // Run the classifier
    EI_IMPULSE_ERROR r = run_classifier(&signal, &result, debug_nn);
    if (r != EI_IMPULSE_OK) {
        ei_printf("ERR: Failed to run classifier (%d)\n", r);
        return;
    }

    // Print the predictions
    ei_printf("Predictions ");
    ei_printf("(DSP: %d ms., Classification: %d ms., Anomaly: %d ms.)",
        result.timing.dsp, result.timing.classification, result.timing.anomaly);
    ei_printf(": \n");
    
    // Find highest prediction and its index
    float highest_value = 0;
    size_t highest_index = 0;
    
    for (size_t ix = 0; ix < EI_CLASSIFIER_LABEL_COUNT; ix++) {
        float value = result.classification[ix].value;
        ei_printf("    %s: ", result.classification[ix].label);
        ei_printf_float(value);
        ei_printf("\n");
        
        if (value > highest_value) {
            highest_value = value;
            highest_index = ix;
        }
    }
    
    // Check if prediction exceeds threshold and trigger servo
    if (highest_index == 0 && highest_value > 0.45) {       //not too mutch confidence, good balance
        ei_printf("Triggering servo movement, confidence: ");
        ei_printf_float(highest_value);
        ei_printf("\n");
        
        // Trigger servo via queue system (non-blocking)
        trigger_servo(2000);
    }
    
#if EI_CLASSIFIER_HAS_ANOMALY == 1
    ei_printf("    anomaly score: ");
    ei_printf_float(result.anomaly);
    ei_printf("\n");
#endif
}

/**
 * Audio inference callback - processes audio data
 * Protected by semaphore for thread safety
 */
static void audio_inference_callback(uint32_t n_bytes)
{
    // Take semaphore before accessing shared buffer
    if (xSemaphoreTake(buffer_semaphore, pdMS_TO_TICKS(100)) != pdTRUE) {
        ei_printf("ERR: Could not take buffer semaphore\n");
        return;
    }
    
    for(int i = 0; i < n_bytes>>1; i++) {
        inference.buffer[inference.buf_count++] = sampleBuffer[i];

        if(inference.buf_count >= inference.n_samples) {
            inference.buf_count = 0;
            inference.buf_ready = 1;
        }
    }
    
    // Release semaphore
    xSemaphoreGive(buffer_semaphore);
}

/**
 * Audio capture task - continuously reads data from I2S
 */
static void capture_samples(void* arg) {
    const int32_t i2s_bytes_to_read = (uint32_t)arg;
    size_t bytes_read = i2s_bytes_to_read;

    while (record_status) {
        // Read data from I2S
        i2s_read(I2S_NUM_0, (void*)sampleBuffer, i2s_bytes_to_read, &bytes_read, 100);

        if (bytes_read <= 0) {
            ei_printf("Error in I2S read: %d", bytes_read);
            vTaskDelay(pdMS_TO_TICKS(10)); // Add delay to prevent CPU hogging
        }
        else {
            if (bytes_read < i2s_bytes_to_read) {
                ei_printf("Partial I2S read: %d bytes", bytes_read);
            }

            // Scale the data (otherwise the sound is too quiet)
            for (int x = 0; x < i2s_bytes_to_read/2; x++) {
                sampleBuffer[x] = (int16_t)(sampleBuffer[x]) * 10;   //amplifying constant 8
            }

            if (record_status) {
                audio_inference_callback(i2s_bytes_to_read);
            }
            else {
                break;
            }
        }
    }
    
    // Task cleanup
    ei_printf("Audio capture task terminated\n");
    vTaskDelete(NULL);
}

/**
 * Start microphone inference - initializes I2S and creates capture task
 */
static bool microphone_inference_start(uint32_t n_samples)
{
    // Allocate memory for inference buffer
    inference.buffer = (int16_t *)malloc(n_samples * sizeof(int16_t));

    if(inference.buffer == NULL) {
        ei_printf("ERR: Failed to allocate memory for inference buffer\n");
        return false;
    }

    // Initialize inference variables
    inference.buf_count  = 0;
    inference.n_samples  = n_samples;
    inference.buf_ready  = 0;

    // Configure I2S for ESP32
    i2s_config_t i2s_config = {
        .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX | I2S_MODE_PDM),
        .sample_rate = 16000,  // 16kHz for speech recognition
        .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
        .channel_format = I2S_CHANNEL_FMT_ONLY_RIGHT,
        .communication_format = I2S_COMM_FORMAT_STAND_I2S,
        .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
        .dma_buf_count = 2,
        .dma_buf_len = 512,  // Buffer size for DMA transfer
    };
    
    // Install I2S driver
    esp_err_t err = i2s_driver_install(I2S_NUM_0, &i2s_config, 0, NULL);
    if (err != ESP_OK) {
        ei_printf("Failed to install I2S driver: %d\n", err);
        // Clean up if I2S installation fails
        free(inference.buffer);
        inference.buffer = NULL;
        return false;
    }
    
    // Configure I2S pins
    i2s_pin_config_t pin_config = {
#if (ESP_IDF_VERSION > ESP_IDF_VERSION_VAL(4, 3, 0))
        .mck_io_num = I2S_PIN_NO_CHANGE,
#endif
        .bck_io_num = CONFIG_I2S_BCK_PIN,
        .ws_io_num = CONFIG_I2S_LRCK_PIN,
        .data_out_num = CONFIG_I2S_DATA_PIN,
        .data_in_num = CONFIG_I2S_DATA_IN_PIN
    };
    
    // Set I2S pins
    err = i2s_set_pin(I2S_NUM_0, &pin_config);
    if (err != ESP_OK) {
        ei_printf("Failed to set I2S pin: %d\n", err);
        // Clean up if setting pins fails
        i2s_driver_uninstall(I2S_NUM_0);
        free(inference.buffer);
        inference.buffer = NULL;
        return false;
    }

    // Allow I2S to stabilize
    ei_sleep(100);

    // Mark recording as active
    record_status = true;

    // Create capture task with reduced stack size (16KB instead of 32KB)
    BaseType_t task_created = xTaskCreate(
        capture_samples,
        "CaptureSamples",
        1024 * 16,           // Reduced stack size (16KB)
        (void*)sample_buffer_size,
        10,
        &captureTaskHandle
    );
    
    if (task_created != pdPASS) {
        ei_printf("ERR: Failed to create capture task\n");
        // Clean up on failure
        i2s_driver_uninstall(I2S_NUM_0);
        free(inference.buffer);
        inference.buffer = NULL;
        return false;
    }

    return true;
}

/**
 * Record function - waits for buffer to be ready
 */
static bool microphone_inference_record(void)
{
    bool ret = true;

    // Wait for buffer to be ready with timeout
    uint32_t timeout_ms = 5000; // 5 second timeout
    uint32_t start_ms = millis();
    
    while (inference.buf_ready == 0) {
        // Check for timeout
        if ((millis() - start_ms) > timeout_ms) {
            ei_printf("ERR: Timeout waiting for audio buffer\n");
            return false;
        }
        delay(10);
    }

    // Take semaphore before accessing shared buffer
    if (xSemaphoreTake(buffer_semaphore, pdMS_TO_TICKS(100)) != pdTRUE) {
        ei_printf("ERR: Could not take buffer semaphore in record function\n");
        return false;
    }
    
    // Reset buffer ready flag
    inference.buf_ready = 0;
    
    // Release semaphore
    xSemaphoreGive(buffer_semaphore);
    
    return ret;
}

/**
 * Convert raw audio data to float for the neural network
 */
static int microphone_audio_signal_get_data(size_t offset, size_t length, float *out_ptr)
{
    // Take semaphore before accessing buffer
    if (xSemaphoreTake(buffer_semaphore, pdMS_TO_TICKS(100)) != pdTRUE) {
        ei_printf("ERR: Could not take buffer semaphore in get_data function\n");
        return -1;
    }
    
    // Convert int16 to float
    numpy::int16_to_float(&inference.buffer[offset], out_ptr, length);
    
    // Release semaphore
    xSemaphoreGive(buffer_semaphore);

    return 0;
}

/**
 * Properly shutdown the inference system
 * Call this function to safely stop recording and free resources
 */
void stop_inference() {
    // Signal the capture task to stop
    record_status = false;
    
    // Wait for the capture task to finish (with timeout)
    uint32_t timeout_ms = 1000;  // 1 second timeout
    uint32_t start_ms = millis();
    
    while (captureTaskHandle != NULL && 
           eTaskGetState(captureTaskHandle) != eDeleted) {
        
        // Check for timeout
        if ((millis() - start_ms) > timeout_ms) {
            ei_printf("WARN: Timeout waiting for capture task to end\n");
            if (captureTaskHandle != NULL) {
                vTaskDelete(captureTaskHandle);
                captureTaskHandle = NULL;
            }
            break;
        }
        
        delay(10);
    }
    
    // Stop the servo task
    if (servoTaskHandle != NULL) {
        vTaskDelete(servoTaskHandle);
        servoTaskHandle = NULL;
        ei_printf("Servo task terminated\n");
    }
    
    // Clean up resources
    microphone_inference_end();
    
    // Delete the synchronization primitives
    if (buffer_semaphore != NULL) {
        vSemaphoreDelete(buffer_semaphore);
        buffer_semaphore = NULL;
    }
    
    if (servoCommandQueue != NULL) {
        vQueueDelete(servoCommandQueue);
        servoCommandQueue = NULL;
    }
    
    ei_printf("Inference system stopped successfully\n");
}

/**
 * Clean up resources when inference ends
 */
static void microphone_inference_end(void)
{
    // Uninstall I2S driver
    i2s_driver_uninstall(I2S_NUM_0);
    
    // Free the buffer memory
    if (inference.buffer != NULL) {
        free(inference.buffer);
        inference.buffer = NULL;
    }
    
    ei_printf("Inference resources released\n");
}

/**
 * Servo control task - processes commands from the queue
 */
static void servo_task(void* arg) {
    ServoCommand_t command;
    
    while (true) {
        // Wait for a command from the queue
        if (xQueueReceive(servoCommandQueue, &command, portMAX_DELAY) == pdTRUE) {
            if (command.activate) {
                ei_printf("Servo task executing movement\n");
                
                // Call the servo function with the specified delay
                servo(command.delayTime);
                
                ei_printf("Servo movement completed\n");
            }
        }
    }
}

/**
 * Function to trigger servo movement via queue
 */
static void trigger_servo(int delayTime) {
    ServoCommand_t command;
    command.activate = true;
    command.delayTime = delayTime;
    
    // Send command to queue (non-blocking with timeout)
    if (xQueueSend(servoCommandQueue, &command, pdMS_TO_TICKS(100)) != pdTRUE) {
        ei_printf("WARN: Failed to send servo command to queue\n");
    }
}

/**
 * Add this function to your code to handle CTRL+C or other shutdown signals
 */
void handleShutdown() {
    ei_printf("Shutting down inference system...\n");
    stop_inference();
}

#if !defined(EI_CLASSIFIER_SENSOR) || EI_CLASSIFIER_SENSOR != EI_CLASSIFIER_SENSOR_MICROPHONE
#error "Invalid model for current sensor."
#endif

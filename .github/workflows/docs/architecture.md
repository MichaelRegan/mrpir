### `mrpir` Project Architecture Documentation

#### **Overview**
The `mrpir` project is a Python application designed to run on a Raspberry Pi 4, utilizing Wayland as the display server and an official Raspberry Pi touchscreen. The application monitors a PIR motion sensor to adjust screen brightness dynamically based on detected motion. It also communicates with Home Assistant using MQTT and includes additional features like turning off the screen after sundown. The architecture is designed with modularity, scalability, and maintainability in mind, incorporating best practices such as dependency injection, robust error handling, and multi-threading.

![architecture diagram](image.png)
---

### **1. High-Level Architecture**
The high-level architecture of the `mrpir` project consists of several core components, each responsible for specific functionalities:

- **Raspberry Pi 4**: The hardware platform on which the application runs. It interfaces with various peripherals like the PIR motion sensor and the official Raspberry Pi touchscreen.
  
- **Wayland Display Server**: Manages the graphical output of the Raspberry Pi, including the touchscreen interface. The `mrpir` application interacts with this server to control screen brightness and other display-related features.

- **PIR Motion Sensor**: Detects motion within its range and sends signals to the Raspberry Pi. The `SensorMonitor` class in the application processes these signals.

- **Official Raspberry Pi Touchscreen**: The display device used by the Raspberry Pi. The `ScreenControl` class manages its brightness based on motion detection.

- **mrpir Application**: The core of the project, comprising multiple modules that handle sensor monitoring, screen control, MQTT communication, and service management. These modules interact with each other to achieve the desired functionality.

- **Home Assistant (MQTT Broker)**: A home automation platform that receives updates from the `mrpir` application via MQTT. It processes these updates to trigger other automation actions as configured by the user.

---

### **2. Core Components**

#### **mrpir Application**

The `mrpir` application is composed of several key modules, each with distinct responsibilities:

1. **`Config` (config.py)**
   - Manages the application's configuration settings, loaded from environment variables (`.env` file) or other sources. 
   - Uses dependency injection to provide configuration data to other modules.

2. **`SensorMonitor` (sensor_monitor.py)**

      **Overview:**
      The `SensorMonitor` class is responsible for monitoring a PIR motion sensor using the `gpiozero` library. It detects motion and no-motion events, triggering registered callbacks for each event. The class is designed to be robust, with error handling for sensor-related issues and a flexible interface for callback registration.

   ***Key Responsibilities:***
   - **Motion Detection:** Monitors the PIR motion sensor and detects motion events.
   - **No Motion Detection:** Identifies when no motion has been detected after a configurable timeout period.
   - **Callback Management:** Allows other components to register callbacks for `on_motion` and `on_no_motion` events.
   - **Manual State Update:** Provides a method to manually check and update the sensor state, ensuring that the application can handle unexpected changes or recheck the sensor state.
   - **Start/Stop Sensor Monitoring:** Provides methods to start and stop monitoring, which are important for resource management and controlled shutdown.

   **Attributes:**
   - **`config` (dict):** Holds configuration settings for the sensor monitor, including the GPIO pin and motion timeout values.
   - **`callbacks` (Dict[str, List[Callable]]):** Stores the lists of callback functions for `on_motion` and `on_no_motion` events.
   - **`motion_detected` (bool):** Tracks whether motion is currently detected.
   - **`last_motion_time` (float):** Records the timestamp of the last detected motion, used to determine if the no-motion timeout has been reached.
   - **`_stop_event` (threading.Event):** A threading event to signal when the sensor monitoring should stop.
   - **`sensor` (MotionSensor):** The motion sensor instance initialized from the `gpiozero` library.

   **Methods:**
   - **`__init__(self, config)`:** Initializes the `SensorMonitor` with the provided configuration. It sets up the motion sensor and prepares for monitoring.
   - **`register_callback(self, key: str, callback: Callable) -> None`:** Registers a callback for the specified event key (`on_motion` or `on_no_motion`).
   - **`start(self) -> None`:** Starts the sensor monitoring by linking sensor events to the appropriate callbacks.
   - **`on_motion(self) -> None`:** Handles the motion detected event, setting the internal state and triggering registered `on_motion` callbacks.
   - **`on_no_motion(self) -> None`:** Handles the no-motion detected event, updating the state and triggering registered `on_no_motion` callbacks.
   - **`update_sensor(self) -> None`:** Manually updates the sensor state, rechecking for motion and triggering the appropriate callbacks.
   - **`stop(self) -> None`:** Stops the sensor monitoring, closing the sensor and freeing resources.

   **Error Handling:**
   - The class includes error handling for operations related to the `gpiozero` library. Errors are logged, and in cases where the sensor fails to initialize or operate correctly, the system can raise an exception or enter a safe state.

   **Usage in the Application:**
   - The `SensorMonitor` integrates with the `ScreenControl` and `MQTTHelper` classes, triggering actions like adjusting screen brightness or notifying Home Assistant based on motion events. The class’s ability to register callbacks makes it flexible and easily extendable.

   **Test Considerations:**
   - Testing should include scenarios for motion detection, no-motion detection, callback invocation, error handling, and the start/stop functionality. Mocking the `gpiozero` library will be essential for isolating sensor behavior in unit tests.


3. **`ScreenControl` (screen_control.py)**
   - Adjusts the brightness of the Raspberry Pi touchscreen based on motion detection.
   - Smoothly transitions screen brightness to 90% upon motion detection and dims it to 0% after a configurable period of no motion.
   - Integrates with the `SundownManager` to turn off the screen after sundown if no motion is detected for an extended period.

4. **`MQTTHelper` (mqtt_helper.py)**
   - Manages MQTT communication with Home Assistant.
   - Publishes updates on the motion state to a specific MQTT topic, enabling Home Assistant to respond to motion or lack thereof.
   - Handles errors in MQTT communication, including retry mechanisms.

5. **`ServiceManager` (service_manager.py)**
   - Manages the integration of the application with systemd, ensuring it runs smoothly as a background service.
   - Uses the `sdnotify` library to notify systemd about the application's status.

---

### **3. Component Interactions**
The components in the `mrpir` application interact with each other and external systems as follows:

- **Sensor Interaction**: The `SensorMonitor`  class is responsible for monitoring a PIR motion sensor using the `gpiozero` library. It detects motion and no-motion events, triggering registered callbacks for each event. The class is designed to be robust, with error handling for sensor-related issues and a flexible interface for callback registration.

- **Screen Control**: The `ScreenControl` adjusts the brightness of the touchscreen based on signals from the `SensorMonitor`. It also communicates with the `SundownManager` to turn off the screen after sundown when no motion is detected for a longer duration.

- **MQTT Communication**: The `MQTTHelper` manages the communication with Home Assistant by publishing the current motion state. This allows Home Assistant to perform actions based on the detected motion or lack thereof.

- **Service Management**: The `ServiceManager` ensures the application runs as a systemd service, allowing it to start automatically on boot and providing status updates to the system.

---

### **4. Multi-Threaded Design**
The `mrpir` application is designed to handle multiple tasks concurrently, ensuring efficient processing of sensor data, screen control, and communication:

- **Main Thread**: Initializes the application, sets up configuration, and starts the other threads.
- **Sensor Monitoring Thread**: Continuously monitors the PIR motion sensor for state changes.
- **Screen Control Thread**: Manages the screen brightness adjustments in response to sensor data.
- **MQTT Communication Thread**: Handles the publishing of motion states to Home Assistant.
- **Service Management Thread**: Manages systemd service integration and status updates.

---

### **5. Error Handling**
Error handling in `mrpir` is robust and distributed across all components:

- **SensorMonitor**: Handles sensor-related errors, including timeouts and hardware failures. Implements retry logic to recover from transient errors.
- **ScreenControl**: Handles errors related to adjusting screen brightness, ensuring that the screen is not left in an undefined state.
- **MQTTHelper**: Implements error handling for MQTT communication failures, including retries and fallback mechanisms to ensure reliable communication with Home Assistant.
- **ServiceManager**: Handles errors related to service management, including failures to notify systemd or issues with starting/stopping the service.

---

### **6. Configuration Management**
Configuration settings for the `mrpir` application are managed through a `.env` file, which is read by the `Config` class. This class loads and validates the configuration settings, ensuring that all required parameters are set correctly. These settings include:

- Motion detection timeout
- Screen brightness levels (e.g., maximum brightness, dim brightness)
- MQTT topics and server details
- GPIO pin configuration for the PIR sensor
- Systemd service-related settings

---

### **7. Logging**
Logging is an essential feature of the `mrpir` application, providing visibility into its operations. The logging configuration is managed through a YAML file (`log_config.yaml`), which is loaded at application startup. Logs include timestamps, severity levels, and messages, and are written to a file or console, depending on the configuration. This helps in debugging and monitoring the application's behavior.

---

### **8. Security Considerations**
Given that `mrpir` communicates with Home Assistant over MQTT, security measures are implemented to protect against unauthorized access and data breaches. These include:

- **TLS Encryption**: Ensures that MQTT communication is encrypted, protecting the integrity and confidentiality of the data.
- **Authentication**: Requires valid credentials to connect to the MQTT broker, preventing unauthorized devices from sending or receiving messages.

---

### **9. Conclusion**
The `mrpir` project's architecture is designed to be modular, scalable, and maintainable, making it easy to extend with new features or adapt to different environments. The use of multi-threading, robust error handling, and clear separation of concerns ensures that the application can handle real-time sensor data and respond quickly to changes in the environment. By following best practices in configuration management, logging, and security, the `mrpir` application is built to be a reliable component of your home automation system.
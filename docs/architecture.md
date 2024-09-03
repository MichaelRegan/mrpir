Thank you for sharing the content of your `architecture.md` file. Based on the provided content and the project updates, here’s an enhanced and revised version of the architecture documentation. I'll add missing sections, improve clarity, and ensure the document is comprehensive.

### `mrpir` Project Architecture Documentation

#### **Overview**
The `mrpir` project is a Python application designed to run on a Raspberry Pi 4, utilizing Wayland as the display server and an official Raspberry Pi touchscreen. The application monitors a PIR motion sensor to dynamically adjust screen brightness based on detected motion. It communicates with Home Assistant using MQTT and includes features like turning off the screen after sundown. The architecture prioritizes modularity, scalability, and maintainability, incorporating best practices such as dependency injection, robust error handling, and multi-threading.

![architecture diagram](image.png)
---

### **1. High-Level Architecture**
The `mrpir` project’s architecture consists of several core components, each with distinct responsibilities:

- **Raspberry Pi 4**: The hardware platform that interfaces with peripherals like the PIR motion sensor and the official Raspberry Pi touchscreen.

- **Wayland Display Server**: Manages graphical output, including the touchscreen interface. The `mrpir` application interacts with Wayland to control screen brightness and other display-related features.

- **PIR Motion Sensor**: Detects motion within its range and sends signals to the Raspberry Pi, processed by the `SensorMonitor` class.

- **Official Raspberry Pi Touchscreen**: The display device managed by the `ScreenControl` class, which adjusts brightness based on motion detection.

- **mrpir Application**: The core of the project, composed of several modules that handle sensor monitoring, screen control, MQTT communication, and service management.

- **Home Assistant (MQTT Broker)**: A home automation platform that receives updates from `mrpir` via MQTT, triggering automation actions configured by the user.

---

### **2. Core Components**

#### **mrpir Application**

The `mrpir` application consists of several key modules:

1. **`Config` (config.py)**
   - **Responsibilities**: Manages application settings, loaded from environment variables or other sources, and provides configuration data to other modules through dependency injection.
   - **Key Functions**: Validates and ensures all required parameters are set, supporting dynamic configurations.

2. **`SensorMonitor` (sensor_monitor.py)**
   - **Overview**: Monitors the PIR motion sensor using the `gpiozero` library, triggering callbacks for motion and no-motion events.
   - **Key Responsibilities**: 
     - Detects motion events and triggers associated actions.
     - Supports callback registration for `on_motion` and `on_no_motion` events.
     - Implements error handling for sensor-related issues and allows manual state updates.
   - **Usage**: Integrates with `ScreenControl` and `MQTTSensorHelper` to adjust screen brightness or notify Home Assistant based on motion events.

3. **`ScreenControl` (screen_control.py)**
   - **Responsibilities**: Adjusts the Raspberry Pi touchscreen brightness based on motion detection. It smoothens brightness transitions and dims the screen after no motion is detected for a configurable period. Integrates with `SundownManager` to turn off the screen after sundown.
   - **Key Functions**: Manages the timing and smooth transition of brightness changes and ensures the screen turns off after an extended period without motion.

4. **`MQTTSensorHelper` (mqtt_helper.py)**
   - **Responsibilities**: Manages MQTT communication with Home Assistant, publishing motion states to a specific MQTT topic, and handling MQTT errors with retry mechanisms.

5. **`ServiceManager` (service_manager.py)**
   - **Responsibilities**: Manages the application as a user service, using the `sdnotify` library to notify systemd of the application’s status, ensuring smooth operation as a background service.

6. **`TimeEvents` (time_events.py)**
   - **Responsibilities**: Schedules and manages time-based events, such as triggering night mode. This module ensures time-dependent actions, like turning off the screen after sundown, are accurately executed.

7. **`Logger` (logger.py)**
   - **Responsibilities**: Configures and manages logging across the application. It ensures that all significant events, errors, and operations are recorded with appropriate log levels (e.g., INFO, DEBUG, ERROR).

---

### **3. Component Interactions**

- **Sensor Interaction**: The `SensorMonitor` detects motion events and triggers actions in the `ScreenControl` and `MQTTSensorHelper` modules.
  
- **Screen Control**: The `ScreenControl` module adjusts the screen’s brightness and power state based on input from the `SensorMonitor` and `TimeEvents` modules, ensuring the screen operates efficiently.

- **MQTT Communication**: `MQTTSensorHelper` communicates with Home Assistant, allowing it to respond to the motion detected by `SensorMonitor`.

- **Service Management**: `ServiceManager` integrates with systemd as a user service, ensuring the application starts on boot and provides status updates.

---

### **4. Multi-Threaded Design**
The application uses multi-threading to handle various tasks concurrently:

- **Main Thread**: Initializes the application, sets up configurations, and starts other threads.
- **Sensor Monitoring Thread**: Continuously monitors the PIR motion sensor for state changes.
- **Screen Control Thread**: Adjusts the screen brightness in response to sensor data.
- **MQTT Communication Thread**: Publishes motion states to Home Assistant.
- **Service Management Thread**: Handles systemd service integration and status updates.

---

### **5. Error Handling**
Error handling is distributed across all components:

- **SensorMonitor**: Handles errors related to sensor operations, including retries for transient failures.
- **ScreenControl**: Manages errors related to screen brightness adjustments, ensuring the screen is never left in an undefined state.
- **MQTTSensorHelper**: Implements robust error handling for MQTT communication, including retry logic.
- **ServiceManager**: Manages errors related to service integration and system notifications.

---

### **6. Configuration Management**
Configuration is handled by the `Config` module, which reads settings from a `.env` file. These settings include:

- Motion detection timeout
- Screen brightness levels
- MQTT server details
- GPIO pin configuration for the PIR sensor
- Time-based settings for night mode

The configuration is validated to ensure that all necessary parameters are present and correct.

---

### **7. Logging**
Logging is managed by the `Logger` module and configured via a YAML file. Logs include timestamps, severity levels, and messages, which can be directed to files or the console. This is crucial for debugging and monitoring application behavior.

---

### **8. Security Considerations**
Security is crucial, particularly in MQTT communication:

- **TLS Encryption**: Ensures MQTT data is encrypted, protecting against interception.
- **Authentication**: Requires valid credentials to connect to the MQTT broker, preventing unauthorized access.

---

### **9. Testing Strategy**
To ensure robustness and reliability, the `mrpir` project employs a comprehensive testing strategy:

- **Unit Tests**: Each module is tested in isolation, with mock objects used to simulate interactions with external components like the GPIO and MQTT broker.
- **Integration Tests**: Modules are tested together to ensure that their interactions work as expected.
- **System Tests**: The complete system is tested on the target hardware (Raspberry Pi) to validate real-world performance.
- **Continuous Integration (CI)**: Automated tests are run on each code commit using CI pipelines, ensuring that the codebase remains stable and that new changes do not introduce regressions.

---

### **10. Conclusion**
The `mrpir` project is architected for flexibility, reliability, and ease of maintenance. Its modular design facilitates easy extension and adaptation, while the use of multi-threading, robust error handling, and secure communication ensures it performs well in real-time environments. With a strong focus on configuration management, logging, and security, `mrpir` is a reliable component for home automation and similar applications.

---

This revised architecture documentation should provide a comprehensive and clear overview of the `mrpir` project, incorporating the latest updates and reflecting best practices in software architecture. Let me know if you need any further adjustments!
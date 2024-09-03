# mrpir - Motion-Activated Screen Control

mrpir is a Python application designed to control the brightness and power state of a screen based on motion detection. It is optimized for use with a Raspberry Pi, a PIR motion sensor, and a connected screen. The application uses MQTT for integration with Home Assistant and features a night mode where the screen is turned off after a period of inactivity.

## Features

- **Motion Detection:** Adjust screen brightness and state based on detected motion.
- **Smooth Brightness Transition:** Gradual changes in screen brightness for a better user experience.
- **Night Mode:** Automatically turn off the screen at night after a configurable period of inactivity.
- **MQTT Integration:** Communicate motion states to Home Assistant via MQTT.
- **User Service Integration:** Designed to run as a user service with watchdog support.

## Installation

### Prerequisites

- Raspberry Pi (or similar device) running a linux distribution with Waland
- PIR Motion Sensor connected to a GPIO pin
- Screen connected and controllable via `wlr-randr`
- Python 3.6+ installed
- Virtual environment for Python recommended

### Setup

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/mrpir.git
   cd mrpir
   ```

2. **Create and Activate a Virtual Environment:**

   On Linux
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
   On Windows
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```


3. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables:**

   Create a `.env` file in the project root and set the necessary environment variables:

    All settings are controlled via the `.env` file. Key configurations include:

    ### Display Settings
    Turning the screen off and on is accomplished with wrl-ranr. A typical command would look like: "wlr-randr --output DSI-1 --on". The screen device can be HDMI-1, DSI-1 for the raspberry Pi official screen, or others. Check the screen options in raspberry pi.

    ```dotenv
    DIM_BRIGHTNESS=0            # The brightness level when dimmed (0-255)
    BRIGHT_BRIGHTNESS=230       # The brightness level when bright (0-255)
    BRIGHTNESS_PATH=            # Example: /sys/class/backlight/[10-0045]/brightness - replace [10-0045] with your screen
    TRANSITION_TIME=2           # Time in seconds for brightness transitions

    SUNDOWN_TIMEOUT-3600        # Seconds after sundown for the screen to turn off
    ```

    ### PIR Sensor settings
    ```dotenv
        GPIO_PIN=23             # GPIO pin connected to the PIR motion sensor
        NO_MOTION_DELAY=5       # Delay in seconds before dimming after no 
    ```

    ### MQTT Settings
    ```dotenv
        MQTT_HOST=""            # MQTT server address as FQDN or IP
        MQTT_PORT=1883          # MQTT server port
        MQTT_USERNAME=""        # MQTT username, leave blank for no username
        MQTT_PASSWORD=""        # MQTT password, leave black for no password
        MQTT_CLIENT_ID=""       # MQTT client ID is a unique string for mqtt
        MQTT_DEVICE=""          # MQTT device identifier such as the rasperry pi name
    ```

    ### Night Mode Settings
    ```dotenv
        SCREEN_OFF_DELAY=3600   # Timeout in seconds before turning off the screen during night mode (1 hour)
        NIGHT_START_HOUR=22     # Hour to start night mode (24-hour format, e.g., 22 for 10 PM)
        NIGHT_END_HOUR=6        # Hour to end night mode (24-hour format, e.g., 6 for 6 AM)
    ```

    ### Time Events
    ```dotenv
        LOCATION_NAME=""        # Friendly name of your location, such as town or city
        REGION=""               # Friendly name of your region, such as county
        LATITUDE=""             # Example coordinates for New York City "40.712776"
        LONGITUDE=""            # Example coordinates for New York City "-74.005974"
    ```

5. **Configure User Service:**

   Update and enable the `mrpir.service` file as a user service:

   Update the following values:

    ExecStart=/full/path/to/venv/python /full/path/to/main.py
    * eg: /home/pi/Projects/mrpir/venv/bin/python /home/pi/Projects/mrpir/main.py

    WorkingDirectory=
    * eg: /home/pi/Projects/mrpir

   ```bash
   mkdir -p ~/.config/systemd/user/
   cp mrpir.service ~/.config/systemd/user/
   systemctl --user daemon-reload
   systemctl --user enable mrpir.service
   systemctl --user start mrpir.service
   ```

   ***Ensure the User Services Start at Boot***

    By default, user services don’t start at boot unless you enable lingering. To ensure that the user services start even after a reboot, you need to enable lingering for your user:

    ```bash
    sudo loginctl enable-linger $USER
    ```
    This command allows user services to start even when no user is logged in.

### Usage Scenarios

- **Home Automation:** Integrate with Home Assistant to control the brightness of a Raspberry Pi screen based on room occupancy, creating a more energy-efficient smart home setup.
- **Nighttime Mode:** Automatically dim or turn off the screen after a specified time at night to avoid unwanted light and save power.
- **Conference Rooms:** Use the application in office environments to automatically manage the screen in conference rooms based on motion detection, ensuring screens are only active when needed.
- **Public Displays:** Deploy in public areas where screens are active only when someone is in proximity, reducing energy consumption and extending screen life.

### Code Structure

- **config.py**: Handles loading environment variables and configurations.
- **main.py**: The entry point of the application that initializes and starts the system components.
- **mqtt_sensor_helper.py**: Manages MQTT communications for motion sensor data.
- **screen_control.py**: Controls the screen brightness and power state.
- **sensor_monitor.py**: Monitors the motion sensor and triggers callbacks based on detected motion or lack thereof.
- **service_manager.py**: Manages the application as a user service, including integration with `sdnotify`.
- **time_events.py**: Schedules and manages time-based events such as night mode transitions.
- **logger.py**: Configures and manages logging for the application.

### Running the Application

To manually start the application:

```bash
python main.py
```

### Logs

Logs are stored in `~/.mrpir/logs`. You can check logs using:

```bash
tail -f ~/.mrpir/logs/mrpir.log
```

### Troubleshooting

- **Service Fails to Start:**
  - Ensure that the service file is correctly placed in `~/.config/systemd/user/`.
  - Run `systemctl --user status mrpir.service` to check the status and identify any errors.

- **Motion Detection Not Working:**
  - Double-check the GPIO pin configuration in the `.env` file to ensure it matches the physical connection.
  - Verify that the PIR sensor is functioning correctly by testing it with a simple Python script.

- **MQTT Communication Issues:**
  - Ensure the MQTT broker details in the `.env` file are correct, including the broker address, port, username, and password.
  - Check network connectivity between the Raspberry Pi and the MQTT broker.

- **Logs Not Appearing:**
  - Verify that the log directory `~/.mrpir/logs` exists and is writable.
  - Check the `LOG_LEVEL` setting in the `.env` file to ensure it's set appropriately (e.g., `INFO`, `DEBUG`).

### Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [GPIO Zero](https://gpiozero.readthedocs.io/) for motion sensor handling.
- [Paho MQTT](https://pypi.org/project/paho-mqtt/) for MQTT communication.
- [SDNotify](https://pypi.org/project/sdnotify/) for systemd notifications.


## Configuration

All settings are controlled via the `.env` file. Key configurations include:

### Display Settings
Turning the screen off and on is accomplished with wrl-ranr. A typical command would look like: "wlr-randr --output DSI-1 --on". The screen device can be HDMI-1, DSI-1 for the raspberry Pi official screen, or others. Check the screen options in raspberry pi.

    DIM_BRIGHTNESS=0        # The brightness level when dimmed (0-255)
    BRIGHT_BRIGHTNESS=230   # The brightness level when bright (0-255)
    BRIGHTNESS_PATH=/sys/class/backlight/[10-0045]/brightness # replace [10-0045] with your screen
    TRANSITION_TIME=2       # Time in seconds for brightness transitions

    SUNDOWN_TIMEOUT-3600    # Seconds after sundown for the screen to turn off

### PIR Sensor settings
    GPIO_PIN=23             # GPIO pin connected to the PIR motion sensor
    NO_MOTION_DELAY=5       # Delay in seconds before dimming after no 

### MQTT Settings
    MQTT_HOST=""            # MQTT server address as FQDN or IP
    MQTT_PORT=1883          # MQTT server port
    MQTT_USERNAME=""        # MQTT username, leave blank for no username
    MQTT_PASSWORD=""        # MQTT password, leave black for no password
    MQTT_CLIENT_ID=""       # MQTT client ID is a unique string for mqtt
    MQTT_DEVICE=""          # MQTT device identifier such as the rasperry pi name

### Night Mode Settings
    SCREEN_OFF_DELAY=3600   # Timeout in seconds before turning off the screen during night mode (1 hour)
    NIGHT_START_HOUR=22     # Hour to start night mode (24-hour format, e.g., 22 for 10 PM)
    NIGHT_END_HOUR=6        # Hour to end night mode (24-hour format, e.g., 6 for 6 AM)

### Time Events
    LOCATION_NAME=""        # Friendly name of your location, such as town or city
    REGION=""               # Friendly name of your region, such as county
    LATITUDE=""             # Example coordinates for New York City "40.712776"
    LONGITUDE=""            # Example coordinates for New York City "-74.005974"
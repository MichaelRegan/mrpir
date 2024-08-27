Here's a draft of the `README.md` file for your project:

---

# mrpir - Motion-Activated Screen Control

mrpir is a Python application designed to control the brightness and power state of a screen based on motion detection. It is optimized for use with a Raspberry Pi, a PIR motion sensor, and a connected screen. The application uses MQTT for integration with Home Assistant and features a night mode where the screen is turned off after a period of inactivity.

## Features

- **Motion Detection:** Adjust screen brightness and state based on detected motion.
- **Smooth Brightness Transition:** Gradual changes in screen brightness for a better user experience.
- **Night Mode:** Automatically turn off the screen at night after a configurable period of inactivity.
- **MQTT Integration:** Communicate motion states to Home Assistant via MQTT.
- **Systemd Integration:** Designed to run as a service with watchdog support.

## Installation

### Prerequisites

- Raspberry Pi (or similar device)
- PIR Motion Sensor connected to a GPIO pin
- Screen connected and controlled via `wlr-randr`
- Python 3.6+ installed
- Virtual environment for Python recommended

### Setup

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/mrpir.git
   cd mrpir
   ```

2. **Create and Activate a Virtual Environment:**

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

   ```dotenv
   DIM_BRIGHTNESS
   BRIGHT_BRIGHTNESS
   TRANSITION_TIME
   NO_MOTION_DELAY
   GPIO_PIN
   BRIGHTNESS_PATH
   MQTT_SERVER
   MQTT_PORT
   MQTT_USER
   MQTT_PASSWORD
   MQTT_CLIENT_ID
   MQTT_DEVICE
   LOG_LEVEL
   NIGHT_MODE_START
   NIGHT_MODE_END
   NIGHT_MODE_TIMEOUT
   ```

5. **Configure Systemd Service:**

   Copy the `mrpir.service` file to `/etc/systemd/system/`:

   ```bash
   cp mrpir.service ~/.config/systemd/user/
   ```
    Edit ~/.config/systemd/user/mrpir.service

    ```bash
    nano ~/.config/systemd/user/mrpir.service
    ```
    Update the following values:

    ExecStart=/full/path/to/venv/python /full/path/to/main/py
    * eg: /home/pi/Projects/mrpir/venv/bin/python /home/pi/Projects/mrpir/main.py

    WorkingDirectory=
    * eg: /home/pi/Projects/mrpir

    EnvironmentFile=
    * eg: /home/pi/Projects/mrpir/.env

   Enable and start the service:

   ```bash
   systemctl --user enable mrpir
   systemctl --user start mrpir
   ```

6. **Enable and Start the User Service**
    
    To start and enable the user service, you need to use the --user flag with systemctl:
    
    Reload the user systemd manager to recognize the new service:
    
    ```bash
    systemctl --user daemon-reload
    ```
    ***Enable the service to start automatically at login:***

    ```bash 
    systemctl --user enable motion_detection.service
    ```
    
    ***Start the service immediately:***

    ```bash
    systemctl --user start motion_detection.service
    ```
7. **Check the Status of the Service**

    You can check the status of the user service with:

    bash
    Copy code
    systemctl --user status motion_detection.service

8. **Ensure the User Services Start at Boot**

    By default, user services don’t start at boot unless you enable lingering. To ensure that the user services start even after a reboot, you need to enable lingering for your user:

    ```bash
    sudo loginctl enable-linger $USER
    ```
    This command allows user services to start even when no user is logged in.

6. **Manage the User Service**

    You can manage the user service similarly to a system service, using the systemctl --user command:

    ***Stop the service:***

    ``` bash
    systemctl --user stop mrpir.service
    ```

    ***Start and restart the service:***

    ```bash
    systemctl --user start mrpir.service
    systemctl --user restart mrpir.service
    ```

    ***Disable the service:***

    ```bash
    systemctl --user disable mrpir.service
    ```

    ***View the system journal***
    ```bash
    journalctl --user -xeu mrpir.service
    journalctl -u mrpir.service -n 100
    ```

## Usage

- The application runs as a systemd service, automatically adjusting screen brightness based on motion.
- During the configured night mode period, the screen will turn off after the specified timeout if no motion is detected.

### Commands

- **Turn Screen On:**

   The screen is automatically turned on when motion is detected.

- **Turn Screen Off:**

   The screen turns off during the night mode period after the configured timeout period of inactivity.

## Configuration

All settings are controlled via the `.env` file. Key configurations include:

### Brightness Settings
    DIM_BRIGHTNESS=0        # The brightness level when dimmed (0-255)
    BRIGHT_BRIGHTNESS=230   # The brightness level when bright (0-255)
    TRANSITION_TIME=2       # Time in seconds for brightness transitions
    NO_MOTION_DELAY=5       # Delay in seconds before dimming after no motion is detected

### GPIO and Screen Settings
    GPIO_PIN=23             # GPIO pin connected to the PIR motion sensor
    BRIGHTNESS_PATH=""      # Path to the brightness control file: /sys/class/backlight/{your_screen}/brightness

### MQTT Settings
    MQTT_SERVER=""      # MQTT server address as FQDN or IP
    MQTT_PORT=1883      # MQTT server port
    MQTT_USER=""        # MQTT username
    MQTT_PASSWORD=""    # MQTT password
    MQTT_CLIENT_ID=""   # MQTT client ID is a unique string for mqtt
    MQTT_DEVICE=""      # MQTT device identifier such as the rasperry pi name

### Logging
    LOG_LEVEL=WARN      # Logging level (DEBUG, INFO, WARN, ERROR)

### Night Mode Settings
    SCREEN_OFF_DELAY=3600   # Timeout in seconds before turning off the screen during night mode (1 hour)
    NIGHT_START_HOUR=22     # Hour to start night mode (24-hour format, e.g., 22 for 10 PM)
    NIGHT_END_HOUR=6        # Hour to end night mode (24-hour format, e.g., 6 for 6 AM)

### Screen Control Commands
    export SCREEN_OFF_COMMAND="wlr-randr --output DSI-1 --off"  # Screen on command
    export SCREEN_ON_COMMAND="wlr-randr --output DSI-1 --on"    # Screen off command


## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [GPIO Zero](https://gpiozero.readthedocs.io/) for motion sensor handling.
- [Paho MQTT](https://pypi.org/project/paho-mqtt/) for MQTT communication.
- [SDNotify](https://pypi.org/project/sdnotify/) for systemd notifications.

---

Feel free to customize the README as needed for your specific project requirements.
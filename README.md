# mrpir
Python script to support a PIR sensor on SBC's and publish over MQTT with Home Assistant discovery support

The following environment variables are used and should be stored in an .env file:
```
MQTT_USER_NAME=xyz
MQTT_PASSWORD=xyz
MQTT_DEVICE=xyz
MQTT_CLIENT_ID=xyz
MQTT_PORT=1883 or other if configured differently
MQTT_BROKER=servername or IP of the MQTT broker
PIR_PIN=signal pin connected to the presense sensor
MQTT_LOGGING=0 or 1 
XSCREENSAVER_SUPPORT=1
LOGGING_LEVEL=1
```

make sure python dependencies are installed:
```
sudo pip3 install PyYAML
sudo pip3 install paho-mqtt
sudo pip3 install python-decouple
```
# Configure a raspberry pi as a KIOSK for Home Assistant
## Create a startup script
1. Edit your crontab list by typing:
sudo crontab -e
You can launch crontab without entering sudo, but if you do, you won’t be able to run scripts that require admin privileges. In fact, you get a different list of crontabs if you don’t use sudo so don’t forget to keep using it or not using it.
2. Add a line at the end of the file that reads like this:
@reboot python3 /home/pi/startup.sh
3. Create the file: /home/pi/startup.sh
4. Run nano startup.sh
5. Add two lines: 
echo "${usb_flag}" | sudo tee /sys/devices/platform/soc/3f980000.usb/buspower >/dev/null
sudo tvservice --off
6. make the startup file executable: sudo chmod a+x startup.sh
## Remove the cursor on the PI screen
sudo sed -i -- "s/#xserver-command=X/xserver-command=X -nocursor/" /etc/lightdm/lightdm.conf
also see: https://raspberrypi.stackexchange.com/questions/53127/how-to-permanently-hide-mouse-pointer-or-cursor-on-raspberry-pi/53813#53813

OR
sudo apt install xdotool unclutter

## Automatically enter the kiosk mode and launch homeassistant url
1. Create a file called mrscreen.desktop (or something else .desktop) in the /etc/xdg/autostart/ directory.
```sudo nano /etc/xdg/autostart/mrscreen1.desktop```
2. Use the following layout in the myapp.desktop file. 
```
[Desktop Entry]
Exec=chromium-browser --noerrdialogs --disable-infobars --ignore-certificate-errors --kiosk https://homeassistant.mjsquared.net
```

## Add xscreensaver
```
sudo apt-get update
apt-cache search xscreensaver*
sudo apt-get install xscreensaver*
```
Run from nvc or on machine, not ssh
```
xhost +local:pi (this will let the mrpir services interact with the screensaver)
```
Test xscreensarver
```
xscreensaver-command -display ":0.0" -activate
xscreensaver-command -display ":0.0" -deactivate
```
## Start mrpir:
```
sudo nano /lib/systemd/system/mrpir.service
```
Past in the followign:
```
[Unit]
Description=Presense sensor
After=multi-user.target
Wants=network-online.target systemd-networkd-wait-online.service

StartLimitIntervalSec=500
StartLimitBurst=15

[Service]
Type=idle
Restart=on-failure
RestartSec=5s

ExecStart=/usr/bin/sudo /usr/bin/python3 /home/pi/mrpir/mrpir.py (Or path to where you installed the service)
User=pi (or another username)

[Install]
WantedBy=multi-user.target
```
Configure the service file with the right permissions
```sudo chmod 644 /lib/systemd/system/sample.service```

Reload and enable the service
```
sudo systemctl daemon-reload
sudo systemctl enable sample.service
```
Reboot just to ensure we are all set
```sudo reboot```

## Checking the log
```journalctl -u mrpir.service -n 100```

### Exit kiosk mode from ssh
```pkill chromium```

import os
#print ("deactivating screensaver")
#os.system("/bin/xscreensaver-command -display host:display.screen")
os.system("/usr/bin/sudo /usr/bin/sudo /usr/bin/xscreensaver-command -display " + '":0.0"' + " -activate >> /home/pi/xtest.log")
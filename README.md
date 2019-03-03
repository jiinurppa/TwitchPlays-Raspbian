# TwitchPlays-Raspbian
'Twitch Plays' setup for Raspbian (headless, some parts are **NES** specific, tested on **Raspberry Pi 3 B+**)

## Raspbian Requirements
From the Rasbperry Pi Configuration tool
1. System → Boot: **To Desktop**
1. Interfaces → VNC: **Enable**

## Disable Display Sleep
1. Run `sudo nano /etc/lightdm/lightdm.conf`
1. Add `xserver-command=X -s 0 dpms` under `[Seat:*]`
1. Save the file with `Ctrl+O` and exit with `Ctrl+X`

## Enable GL Driver
1. Run `sudo raspi-config`
1. Select **Advanced Options**
1. Select **GL Driver**
1. Select **Legacy**
1. Reboot

## Install Software
1. Run `sudo apt-get install ffmpeg`
1. Run `sudo apt-get install retroarch`
1. Run `sudo apt-get install xdotool`

## Configure Retroarch
These options can be changed from Retroarch's GUI or `~/.config/retroarch/retroarch.cfg`
1. Set **audio** driver to `alsa` (`audio_driver = "alsa"`)
1. Set **input** driver to `x` (`input_driver = "x"`)
1. Set **video** driver to `gl` (`video_driver = "gl"`)
1. Set **record** driver to `ffmpeg` (`record_driver = "ffmpeg"`)
1. Set controls:
   1. Set **Select** as `a` (`input_player1_select = "a"`)   
   1. Set **Start** as `s` (`input_player1_start = "s"`)
1. Download `nestopia_libretro.so` (for **NES** emulation, FCEUmm had input problems)
1. Download a ROM (Retroarch has some homebrew available for download)

If you can't download anything from Retroarch also set `core_updater_buildbot_url = "http://buildbot.libretro.com/nightly/linux/armv7-neon-hf/latest/"`.

## Save Streaming Configuration
* Save the following as `twitch.cfg`:
```
vcodec = libx264
acodec = aac
pix_fmt = yuv420p
scale_factor = 1
threads = 2
video_crf = 25
video_preset = superfast
video_tune = animation
audio_global_quality = 75
sample_rate = 44100
format = flv
```

## Reading Input From Twitch Chat
1. Save the following script as `twitch.py`:
```python
import socket
import sys
import re

class Twitch:

    user = "";
    oauth = "";
    s = None;

    def twitch_login_status(self, data):
        if not re.match(r'^:(testserver\.local|tmi\.twitch\.tv) NOTICE \* :Login unsuccessful\r\n$', data): return True
        else: return False

    def twitch_connect(self, user, key):
        self.user = user;
        self.oauth= key;
        print("Connecting to twitch.tv");
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
        s.settimeout(0.6);
        connect_host = "irc.twitch.tv";
        connect_port = 6667;
        try:
            s.connect((connect_host, connect_port));
        except:
            print("Failed to connect to twitch");
            sys.exit();
        print("Connected to twitch");
        print("Sending our details to twitch...");
        s.send('USER %s\r\n' % user);
        s.send('PASS %s\r\n' % key);
        s.send('NICK %s\r\n' % user);

        if not self.twitch_login_status(s.recv(1024)):
            print("... and they didn't accept our details");
            sys.exit();
        else:
            print("... they accepted our details");
            print("Connected to twitch.tv!")
            self.s = s;
            s.send('JOIN #%s\r\n' % user)
            s.recv(1024);

    def check_has_message(self, data):
        return re.match(r'^:[a-zA-Z0-9_]+\![a-zA-Z0-9_]+@[a-zA-Z0-9_]+(\.tmi\.twitch\.tv|\.testserver\.local) PRIVMSG #[a-zA-Z0-9_]+ :.+$', data)

    def parse_message(self, data):
        return {
            'channel': re.findall(r'^:.+\![a-zA-Z0-9_]+@[a-zA-Z0-9_]+.+ PRIVMSG (.*?) :', data)[0],
            'username': re.findall(r'^:([a-zA-Z0-9_]+)\!', data)[0],
            'message': re.findall(r'PRIVMSG #[a-zA-Z0-9_]+ :(.+)', data)[0].decode('utf8')
        }

    def twitch_recieve_messages(self, amount=1024):
        data = None
        try: data = self.s.recv(1024);
        except: return False;

        if not data:
            print("Lost connection to Twitch, attempting to reconnect...");
            self.twitch_connect(self.user, self.oauth);
            return None

        if data.startswith("PING"):
            self.s.send("PONG " + data.split(" ", 3)[1] + "\r\n");
            return None;

        if self.check_has_message(data):
            return [self.parse_message(line) for line in filter(None, data.split('\r\n'))];

```
2. Save the following script as `letsplay.py`:
```python
import re
import time
import twitch
import subprocess
from subprocess import check_output

def press_key(key):
	subprocess.call("xdotool keydown " + key + " sleep 0.01 keyup " + key, shell=True);
	return;

t = twitch.Twitch();
wid = re.findall("[0-9]+", subprocess.check_output("export DISPLAY=:0 && xdotool search --name \"retroarch\"", shell=True))[0];
subprocess.call("xdotool windowactivate " + wid, shell=True);

#Enter your twitch username and oauth-key below
username = "username";
key = "oauth:key";
t.twitch_connect(username, key);
 
#The main loop
while True:
    #Check for new mesasages
    new_messages = t.twitch_recieve_messages();
 
    if not new_messages:
        #No message
	time.sleep(0.002)
        continue
    else:
        for message in new_messages:
            #Wuhu we got a message. Let's extract some details from it
            msg = message['message'].lower()
            username = message['username'].lower()
 
            #Change this to make Twitch fit to your game!
            if msg.startswith("!a"): press_key("X");
            if msg.startswith("!b"): press_key("Z");
            if msg.startswith("!l"): press_key("Left");
            if msg.startswith("!r"): press_key("Right");
            if msg.startswith("!u"): press_key("Up");
            if msg.startswith("!d"): press_key("Down");
            if msg.startswith("!start"): press_key("S");
            if msg.startswith("!select"): press_key("A");

```
3. Set your username (line 15) and OAuth token (line 16)

The above scripts are adaptations of `twitch.py` and `main.py` found here: http://www.wituz.com/make-your-own-twitch-plays-stream.html

## (Optional) Power Saving
* Disconnect all USB devices
* Disable HDMI `sudo tvservice --off`
* Disable bluetooth `sudo rfkill block bluetooth`
* If you're using ethernet, turn off wifi `sudo rfkill block wifi`
* If you're using wifi, turn off ethernet (and USB) `echo '1-1' > /sys/bus/usb/drivers/usb/unbind`

## Running
1. Open your Raspbian desktop via VNC
1. Open Terminal with two tabs (`Shift+Ctrl+T` for new tab)
1. In first tab run (with your Twitch stream key and ROM path) `retroarch -L ~/.config/retroarch/cores/nestopia_libretro.so --recordconfig ~/twitch.cfg --record rtmp://live.twitch.tv/app/stream_key_here ~/rom.nes`
1. In second tab run `python letsplay.py`
1. Close VNC and enjoy your Twitch Plays stream

Run Retroarch with option `-v` if you encounter problems to see logging.

## Chat Commands
See/modify `letsplay.py`. Defaults are:

|Button  | Command   |
|------- | --------- |
| A      | `!a`      |
| B      | `!b`      |
| Select | `!select` |
| Start  | `!start`  |
| Up     | `!u`      |
| Down   | `!d`      |
| Left   | `!l`      |
| Right  | `!r`      |

Commands will also work with any suffix, so `!u` and `!up` have the same function.

import re
import subprocess
import time
import twitch


def press_key(key_to_press):
    subprocess.call(f"xdotool keydown {key_to_press} sleep 0.01 keyup {key_to_press}", shell=True)
    return


t = twitch.Twitch()
cmd = "export DISPLAY=:0 && xdotool search --name \"retroarch\""
wid = re.findall("[0-9]+", subprocess.check_output(cmd, shell=True))[0]
subprocess.call(f"xdotool windowactivate {wid}", shell=True)

# Enter your twitch username and oauth-key below
username = "username"
key = "oauth:key"
t.twitch_connect(username, key)

# The main loop
while True:
    # Check for new messages
    new_messages = t.twitch_recieve_messages()

    if not new_messages:
        # No message
        time.sleep(0.002)
        continue
    else:
        for message in new_messages:
            # Got a message, let's extract some details from it
            msg = message['message'].lower()
            username = message['username'].lower()

            # Change this to make Twitch fit to your game!
            if msg.startswith("!a"):
                press_key("X")
            if msg.startswith("!b"):
                press_key("Z")
            if msg.startswith("!l"):
                press_key("Left")
            if msg.startswith("!r"):
                press_key("Right")
            if msg.startswith("!u"):
                press_key("Up")
            if msg.startswith("!d"):
                press_key("Down")
            if msg.startswith("!start"):
                press_key("S")
            if msg.startswith("!select"):
                press_key("A")

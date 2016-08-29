from gpiozero import Robot
from evdev import InputDevice, list_devices, ecodes

robot = Robot(left=(4, 14), right=(17, 18))

devices = [InputDevice(device) for device in list_devices()]
keyboard = devices[0]  # this may vary

keypress_actions = {
    ecodes.KEY_UP: robot.forward,
    ecodes.KEY_DOWN: robot.backward,
    ecodes.KEY_LEFT: robot.left,
    ecodes.KEY_RIGHT: robot.right,
}

for event in keyboard.read_loop():
    if event.type == ecodes.EV_KEY:
        if event.value == 1:  # key down
            keypress_actions[event.code]()
        if event.value == 0:  # key up
            robot.stop()

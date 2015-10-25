# Recipes

*Note that reaching the end of a Python file will terminate the process and
GPIOs may be reset. Keep your program alive with `signal.pause` - see the
[notes](notes.md) page for more information.*

## LED

Turn an LED on and off repeatedly:

```python
from gpiozero import LED
from time import sleep

red = LED(2)

while True:
    red.on()
    sleep(1)
    red.off()
    sleep(1)
```

Alternatively:

```python
from gpiozero import LED
from signal import pause

red = LED(2)

red.blink()
pause()
```

## Button

Check if a button is pressed:

```python
from gpiozero import Button

button = Button(4)

while True:
    if button.is_pressed:
        print("Button is pressed")
    else:
        print("Button is not pressed")
```

Wait for a button to be pressed before continuing:

```python
from gpiozero import Button

button = Button(4)

button.wait_for_press()
print("Button was pressed")
```

Run a function every time the button is pressed:

```python
from gpiozero import Button
from signal import pause

def say_hello():
    print("Hello!")

button = Button(4)

button.when_pressed = say_hello
pause()
```

## Button controlled LED

Turn on an LED when a button is pressed:

```python
from gpiozero import LED, Button
from signal import pause

led = LED(2)
button = Button(3)

button.when_pressed = led.on
button.when_released = led.off

pause()
```

## Traffic Lights

A full traffic lights system.

Using a Traffic Lights kit like Pi-Stop:

```python
from gpiozero import TrafficLights
from time import sleep

lights = TrafficLights(2, 3, 4)

lights.green.on()

while True:
    sleep(10)
    lights.green.off()
    lights.amber.on()
    sleep(1)
    lights.amber.off()
    lights.red.on()
    sleep(10)
    lights.amber.on()
    sleep(1)
    lights.green.on()
    lights.amber.off()
    lights.red.off()
```

Using components:

```python
from gpiozero import LED
from time import sleep

red = LED(2)
amber = LED(3)
green = LED(4)

green.on()
amber.off()
red.off()

while True:
    sleep(10)
    green.off()
    amber.on()
    sleep(1)
    amber.off()
    red.on()
    sleep(10)
    amber.on()
    sleep(1)
    green.on()
    amber.off()
    red.off()
```

## Push button stop motion

Capture a picture with the camera module every time a button is pressed:

```python
from gpiozero import Button
from picamera import PiCamera

button = Button(17)

with PiCamera() as camera:
    camera.start_preview()
    frame = 1
    while True:
        button.wait_for_press()
        camera.capture('/home/pi/frame%03d.jpg' % frame)
        frame += 1
```

See
[Push Button Stop
Motion](https://www.raspberrypi.org/learning/quick-reaction-game/) for a full
resource.

## Reaction Game

When you see the light come on, the first person to press their button wins!

```python
from gpiozero import Button, LED
from time import sleep
import random

led = LED(4)

player_1 = Button(2)
player_2 = Button(3)

time = random.uniform(5, 10)
sleep(time)
led.on()

while True:
    if player_1.is_pressed:
        print("Player 1 wins!")
        break
    if player_2.is_pressed:
        print("Player 2 wins!")
        break

led.off()
```

See
[Quick Reaction Game](https://www.raspberrypi.org/learning/quick-reaction-game/)
for a full resource.

## GPIO Music Box

Each button plays a different sound!

```python
from gpiozero import Button
import pygame.mixer
from pygame.mixer import Sound

pygame.mixer.init()

def play(pin):
    sound = sound_pins[pin]
    print("playing note from pin %s" % pin)
    sound.play()

sound_pins = {
    2: Sound("samples/drum_tom_mid_hard.wav"),
    3: Sound("samples/drum_cymbal_open.wav"),
}

buttons = [Button(pin) for pin in sound_pins]
for button in buttons:
    sound = sound_pins[button.pin]
    button.when_pressed = sound.play
```

See [GPIO Music Box](https://www.raspberrypi.org/learning/gpio-music-box/)
for a full resource.

## All on when pressed

While the button is pressed down, the buzzer and all the lights come on.

FishDish:

```python
from gpiozero import FishDish

fish = FishDish()

fish.button.when_pressed = fish.on
fish.button.when_released = fish.off
```

Ryanteck Traffic HAT:

```python
from gpiozero import TrafficHat

th = TrafficHat()

th.button.when_pressed = th.on
th.button.when_released = th.off
```

Using components:

```python
from gpiozero import LED, Buzzer, Button

button = Button(2)
buzzer = Buzzer(3)
red = LED(4)
amber = LED(5)
green = LED(6)

things = [red, amber, green, buzzer]

def things_on():
    for thing in things:
        thing.on()

def things_off():
    for thing in things:
        thing.off()

button.when_pressed = things_on
button.when_released = things_off
```

## RGB LED

Making colours with an RGB LED:

```python
from gpiozero import RGBLED
from time import sleep

led = RGBLED(red=9, green=10, blue=11)

led.red = 1  # full red
led.red = 0.5  # half red

led.rgb = (0, 1, 0)  # full green

led.rgb = (1, 0, 1)  # magenta
led.rgb = (1, 1, 0)  # yellow
led.rgb = (0, 1, 1)  # cyan
led.rgb = (1, 1, 1)  # white

led.rgb = (0, 0, 0)  # off

# slowly increase intensity of blue
for n in range(100):
    led.blue += 0.01
    sleep(0.1)
```

## Motion Sensor

Light an LED when motion is detected:

```python
from gpiozero import MotionSensor, LED

pir = MotionSensor(5)
led = LED(16)

pir.when_motion = led.on
pir.when_no_motion = led.off
```

## Light Sensor

Wait for light and dark:

```python
from gpiozero import LightSensor

sensor = LightSensor(18)

while True:
    sensor.wait_for_light()
    print("It's light! :)")
    sensor.wait_for_dark()
    print("It's dark :(")
```

Run a function when the light changes:

```python
from gpiozero import LightSensor, LED

sensor = LightSensor(18)
led = LED(16)

sensor.when_dark = led.on
sensor.when_light = led.off
```

## Motors

Spin a motor around forwards and backwards:

```python
from gpiozero import Motor
from time import sleep

motor = Motor(forward=4, back=14)

while True:
    motor.forward()
    sleep(5)
    motor.backward()
    sleep(5)
```

## Robot

Make a robot drive around in (roughly) a square:

```python
from gpiozero import Robot
from time import sleep

robot = Robot(left=(4, 14), right=(17, 18))

for i in range(4):
    robot.forward()
    sleep(10)
    robot.right()
    sleep(1)
```

## Button controlled Robot

Use four GPIO buttons as forward/back/left/right controls for a robot:

```python
from gpiozero import RyanteckRobot, Button
from signal import pause

robot = RyanteckRobot()

left = Button(26)
right = Button(16)
fw = Button(21)
bw = Button(20)

fw.when_pressed = robot.forward
fw.when_released = robot.stop

left.when_pressed = robot.left
left.when_released = robot.stop

right.when_pressed = robot.right
right.when_released = robot.stop

bw.when_pressed = robot.backward
bw.when_released = robot.stop

pause()
```

## Keyboard controlled Robot

Use up/down/left/right keys to control a robot:

```python
from gpiozero import RyanteckRobot
from evdev import InputDevice, list_devices, ecodes

robot = RyanteckRobot()

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
```

## Motion Sensor Robot

Make a robot drive forward when it detects motion:

```python
from gpiozero import Robot, MotionSensor

robot = Robot(left=(4, 14), right=(17, 18))
pir = MotionSensor(5)

pir.when_motion = robot.forward
pir.when_no_motion = robot.stop
```

## Potentiometer

Continually print the value of a potentiometer (values between 0 and 1):

```python
from gpiozero import MCP3008

while True:
    with MCP3008(channel=0) as pot:
        print(pot.read())
```

## Full Colour LED controlled by 3 Potentiometers

Wire up three potentiometers (for red, green and blue) and use each of their
values to make up the colour of the LED:

```python
from gpiozero import RGBLED, MCP3008

led = RGBLED(red=2, green=3, blue=4)
red_pot = MCP3008(channel=0)
green_pot = MCP3008(channel=1)
blue_pot = MCP3008(channel=2)

while True:
    led.red = red_pot.value
    led.green = green_pot.value
    led.blue = blue_pot.value
```

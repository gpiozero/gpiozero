# Recipes

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

red = LED(2)

red.blink()
```

## Button

Check if a button is pressed:

```python
from gpiozero import Button

button = Button(4)

if button.is_active:
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

def say_hello():
    print("Hello!")

button = Button(4)

button.when_pressed = say_hello
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
amber = LED(2)
green = LED(2)

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
from gpiozero import button
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

See [Quick Reaction Game](https://www.raspberrypi.org/learning/quick-reaction-game/) for a full resource.

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

See [GPIO Music Box](https://www.raspberrypi.org/learning/gpio-music-box/) for a full resource.

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

Drive two motors forwards for 5 seconds:

```python
from gpiozero import Motor
from time import sleep

left_motor = Motor(7)
right_motor = Motor(8)

left_motor.on()
right_motor.on()
sleep(5)
left_motor.off()
right_motor.off()
```

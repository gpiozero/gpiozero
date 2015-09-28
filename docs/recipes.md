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

## Buzzer

Turn a buzzer on and off repeatedly:

```python
from gpiozero import Buzzer
from time import sleep

buzzer = Buzzer(3)

while True:
    buzzer.on()
    sleep(1)
    buzzer.off()
    sleep(1)
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

def warning():
    print("Don't push the button!")

button = Button(4)

button.when_pressed = warning
```

## Motion Sensor

Detect motion and light an LED when it's detected:

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

## Temperature Sensor

Retrieve light sensor value:

```python
from gpiozero import TemperatureSensor

temperature = TemperatureSensor(6)

print(temperature.value)
```

## Motor

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

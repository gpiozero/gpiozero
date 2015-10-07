# Add-on boards and accessories

These additional interfaces have been provided to group collections of components together for ease of use, and as examples. They are made up of components from the various [input devices](inputs.md) and [output devices](outputs.md) provided by `gpiozero`. See those pages for more information on using components individually.

*Note all GPIO pin numbers use BCM numbering. See the [notes](notes.md) page for more information.*

## LED Board

A Generic LED Board or collection of LEDs.

### Code

Ensure the `LEDBoard` class is imported at the top of the file:

```python
from gpiozero import LEDBoard
```

Create an `LEDBoard` object by passing in a list of the LED pin numbers:

```python
leds = LEDBoard([2, 3, 4, 5, 6])
```

### Methods

| Method | Description | Arguments |
| ------ | ----------- | --------- |
| `on()`     | Turn all the LEDs on. | None |
| `off()`    | Turn all the LEDs off. | None |
| `toggle()` | Toggle all the LEDs. For each LED, if it's on, turn it off; if it's off, turn it on. | None |
| `blink()`  | Make the LEDs turn on and off repeatedly. | `on_time` - The amount of time (in seconds) for the LED to be on each iteration. Default: `1` |
|            |                                           | `off_time` - The amount of time (in seconds) for the LED to be off each iteration. Default: `1` |
|            |                                           | `n` - The number of iterations. `None` means infinite. Default: `None` |
|            |                                           | `background` - If True, start a background thread to continue blinking and return immediately. If False, only return when the blink is finished (warning: the default value of n will result in this method never returning). Default: `True` |

### Properties

| Property | Description | Type |
| -------- | ----------- | ---- |
| `leds`   | A collection of LEDs to access each one individually, or to iterate over them in sequence. | Tuple |

## Traffic Lights

Generic Traffic Lights set.

### Code

Ensure the `TrafficLights` class is imported at the top of the file:

```python
from gpiozero import TrafficLights
```

Create a `TrafficLights` object by passing in the LED pin numbers by name:

```python
traffic = TrafficLights(red=2, amber=3, green=4)
```

or just in order (red, amber, green):

```python
traffic = TrafficLights(2, 3, 4)
```

### Methods

| Method | Description | Arguments |
| ------ | ----------- | --------- |
| `on()` | Turn all three LEDs on. | None |
| `off()` | Turn all three LEDs off. | None |
| `toggle()` | Toggle all three LEDs. For each LED, if it's on, turn it off; if it's off, turn it on. | None |
| `blink()`  | Make the LEDs turn on and off repeatedly. | `on_time` - The amount of time (in seconds) for the LED to be on each iteration. Default: `1` |
|            |                                           | `off_time` - The amount of time (in seconds) for the LED to be off each iteration. Default: `1` |
|            |                                           | `n` - The number of iterations. `None` means infinite. Default: `None` |
|            |                                           | `background` - If True, start a background thread to continue blinking and return immediately. If False, only return when the blink is finished (warning: the default value of n will result in this method never returning). Default: `True` |

### Properties

| Property | Description | Type |
| -------- | ----------- | ---- |
| `red`    | Direct access to the red light as a single `LED` object. | LED |
| `amber`  | Direct access to the amber light as a single `LED` object. | LED |
| `green`  | Direct access to the green light as a single `LED` object. | LED |
| `leds`   | A collection of LEDs to access each one individually, or to iterate over them in sequence. | Tuple |

## PiLITEr

Ciseco Pi-LITEr: strip of 8 very bright LEDs.

### Code

Ensure the `PiLiter` class is imported at the top of the file:

```python
from gpiozero import PiLiter
```

Create a `PiLiter` object:

```python
lite = PiLiter()
```

### Methods

| Method | Description | Arguments |
| ------ | ----------- | --------- |
| `on()` | Turn all eight LEDs on. | None |
| `off()` | Turn all eight LEDs off. | None |
| `toggle()` | Toggle all eight LEDs. For each LED, if it's on, turn it off; if it's off, turn it on. | None |
| `blink()`  | Make all the LEDs turn on and off repeatedly. | `on_time` - The amount of time (in seconds) for the LED to be on each iteration. Default: `1` |
|            |                                               | `off_time` - The amount of time (in seconds) for the LED to be off each iteration. Default: `1` |
|            |                                               | `n` - The number of iterations. `None` means infinite. Default: `None` |
|            |                                               | `background` - If True, start a background thread to continue blinking and return immediately. If False, only return when the blink is finished (warning: the default value of n will result in this method never returning). Default: `True` |

### Properties

| Property | Description | Type |
| -------- | ----------- | ---- |
| `leds`   | A collection of LEDs to access each one individually, or to iterate over them in sequence. | Tuple |

## PI-TRAFFIC

Low Voltage Labs PI-TRAFFIC: vertical traffic lights board on pins 9, 10 and 11.

Ensure the `PiTraffic` class is imported at the top of the file:

```python
from gpiozero import PiTraffic
```

Create a `PiTraffic` object:

```python
traffic = PiTraffic()
```

`PiTraffic` provides an identical interface to the generic `TrafficLights` interface, without the need to specify the pin numbers to be used.

To use the PI-TRAFFIC board on another set of pins, just use the generic `TrafficLights` interface.

### Methods

| Method | Description | Arguments |
| ------ | ----------- | --------- |
| `on()`     | Turn all three LEDs on.  | None |
| `off()`    | Turn all three LEDs off. | None |
| `toggle()` | Toggle all three LEDs. For each LED, if it's on, turn it off; if it's off, turn it on. | None |
| `blink()`  | Make the LEDs turn on and off repeatedly. | `on_time` - The amount of time (in seconds) for the LED to be on each iteration. Default: `1` |
|            |                                           | `off_time` - The amount of time (in seconds) for the LED to be off each iteration. Default: `1` |
|            |                                           | `n` - The number of iterations. `None` means infinite. Default: `None` |
|            |                                           | `background` - If True, start a background thread to continue blinking and return immediately. If False, only return when the blink is finished (warning: the default value of n will result in this method never returning). Default: `True` |

### Properties

| Property | Description | Type |
| -------- | ----------- | ---- |
| `red`    | Direct access to the red light as a single `LED` object. | LED |
| `amber`  | Direct access to the amber light as a single `LED` object. | LED |
| `green`  | Direct access to the green light as a single `LED` object. | LED |
| `leds`   | A collection of LEDs to access each one individually, or to iterate over them in sequence. | Tuple |

## Fish Dish

Pi Supply Fish Dish: traffic light LEDs, a button and a buzzer.

### Code

Ensure the `FishDish` class is imported at the top of the file:

```python
from gpiozero import FishDish
```

Create a `FishDish` object:

```python
fish = FishDish()
```

### Methods

| Method | Description | Arguments |
| ------ | ----------- | --------- |
| `on()`            | Turn all the board's output components on.  | None |
| `off()`           | Turn all the board's output components off. | None |
| `toggle()`        | Toggle all the board's output components. For each component, if it's on, turn it off; if it's off, turn it on. | None || `toggle()` | Toggle all the LEDs. For each LED, if it's on, turn it off; if it's off, turn it on. | None |
| `blink()`         | Make the LEDs turn on and off repeatedly.   | `on_time` - The amount of time (in seconds) for the LED to be on each iteration. Default: `1` |
|                   |                                             | `off_time` - The amount of time (in seconds) for the LED to be off each iteration. Default: `1` |
|                   |                                             | `n` - The number of iterations. `None` means infinite. Default: `None` |
|                   |                                             | `background` - If True, start a background thread to continue blinking and return immediately. If False, only return when the blink is finished (warning: the default value of n will result in this method never returning). Default: `True` |
| `lights_on()`     | Turn all three LEDs on.  | None |
| `lights_off()`    | Turn all three LEDs off. | None |
| `toggle_lights()` | Toggle all the board's LEDs. For each LED, if it's on, turn it off; if it's off, turn it on. | None |
| `blink_lights()`  | Make the board's LEDs turn on and off repeatedly. | `on_time` - The amount of time (in seconds) for the LED to be on each iteration. Default: `1` |
|                   |                                                   | `off_time` - The amount of time (in seconds) for the LED to be off each iteration. Default: `1` |
|                   |                                                   | `n` - The number of iterations. `None` means infinite. Default: `None` |
|                   |                                                   | `background` - If True, start a background thread to continue blinking and return immediately. If False, only return when the blink is finished (warning: the default value of n will result in this method never returning). Default: `True` |

### Properties

| Property | Description | Type |
| -------- | ----------- | ---- |
| `red`    | Direct access to the red light as a single `LED` object. | LED |
| `amber`  | Direct access to the amber light as a single `LED` object. | LED |
| `green`  | Direct access to the green light as a single `LED` object. | LED |
| `buzzer` | Direct access to the buzzer as a single `Buzzer` object. | LED |
| `button` | Direct access to the button as a single `Button` object. | LED |
| `leds`   | A collection of LEDs to access each one individually, or to iterate over them in sequence. | Tuple |
| `all`    | A collection of the board's output components to access each one individually, or to iterate over them in sequence. | Tuple |

## Traffic HAT

Ryanteck Traffic HAT: traffic light LEDs, a button and a buzzer.

### Code

Ensure the `TrafficHat` class is imported at the top of the file:

```python
from gpiozero import TrafficHat
```

Create a `TrafficHat` object by passing in the LED pin numbers by name:

```python
traffic = TrafficHat()
```

The interface is identical to the `FishDish`

## Robot

Generic two-motor robot.

### Code

Ensure the `Robot` class is imported at the top of the file:

```python
from gpiozero import Robot
```

Create a `Robot` object by passing in the pin numbers of the forward and back pairs for each motor:

```python
robot = Robot(left=(4, 14), right=(17, 18))
```

### Methods

| Method | Description | Arguments |
| ------ | ----------- | --------- |
| `forward()` | Drive the robot forwards. | `seconds` - The number of seconds to drive for. If `None`, stay on. Default: `None` |
| `backward()` | Drive the robot backwards. | `seconds` - The number of seconds to drive for. If `None`, stay on. Default: `None` |
| `left()` | Make the robot turn left. | `seconds` - The number of seconds to turn for. If `None`, stay on. Default: `None` |
| `right()` | Make the robot turn right. | `seconds` - The number of seconds to turn for. If `None`, stay on. Default: `None` |
| `stop()` | Stop the robot. | None |

## Ryanteck MCB Robot

Generic robot controller with pre-configured pin numbers.

Same interface as generic `Robot` class, without the need to configure pins:

```python
from gpiozero import RyanteckRobot

robot = RyanteckRobot()
```

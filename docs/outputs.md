# Output Devices

These output device component interfaces have been provided for simple use of everyday components.

Components must be wired up correctly before used in code.

*Note all GPIO pin numbers use BCM numbering. See the [notes](notes.md) page for more information.*

## LED

An LED (Light emitting diode) component.

### Wiring

...

### Code

Ensure the `LED` class is imported at the top of the file:

```python
from gpiozero import LED
```

Create an `LED` object by passing in the pin number the LED is connected to:

```python
led = LED(2)
```

### Methods

| Method | Description | Arguments |
| ------ | ----------- | --------- |
| `on()` | Turn the LED on. | None |
| `off()` | Turn the LED off. | None |
| `toggle()` | Toggle the LED. If it's on, turn it off; if it's off, turn it on. | None |
| `blink()` | Make the LED turn on and off repeatedly. | `on_time=1`, `off_time=1`, `n=1`, `background=True` |

### Properties

| Property | Description | Type |
| -------- | ----------- | ---- |
| `pin`    | The GPIO pin number the LED is connected to. | Integer |
| `is_active` | The current state of the pin (`True` if on; `False` if off). | Boolean |

## Buzzer

A digital Buzzer component.

### Wiring

...

### Code

Ensure the `Buzzer` class is imported at the top of the file:

```python
from gpiozero import Buzzer
```

Create a `Buzzer` object by passing in the pin number the buzzer is connected to:

```python
buzzer = Buzzer(3)
```

### Methods

| Method | Description | Arguments |
| ------ | ----------- | --------- |
| `on()` | Turn the buzzer on. | None |
| `off()` | Turn the buzzer off. | None |
| `toggle()` | Toggle the buzzer. If it's on, turn it off; if it's off, turn it on. | None |
| `blink()` | Make the buzzer turn on and off repeatedly. | `on_time=1`, `off_time=1`, `n=1`, `background=True` |

### Properties

| Property | Description | Type |
| -------- | ----------- | ---- |
| `pin`    | The GPIO pin number the buzzer is connected to. | Integer |
| `is_active` | The current state of the pin (`True` if on; `False` if off). | Boolean |

## RGB LED

A full colour LED component (made up of Red, Green and Blue LEDs).

### Wiring

...

### Code

Ensure the `RGBLED` class is imported at the top of the file:

```python
from gpiozero import RGBLED
```

Create a `RGBLED` object by passing in the LED pin numbers by name:

```python
led = RGBLED(red=2, green=3, blue=4)
```

or just in order (red, green, blue):

```python
led = RGBLED(2, 3, 4)
```

### Methods

| Method | Description | Arguments |
| ------ | ----------- | --------- |
| `on()` | Turn all the LEDs on (makes white light). | None |
| `off()` | Turn all the LEDs off. | None |

### Properties

| Property | Description | Type |
| -------- | ----------- | ---- |
| `red`    | The brightness value of the red LED (0 to 100).     | Integer |
| `green`  | The brightness value of the green LED (0 to 100).   | Integer |
| `blue`   | The brightness value of the blue LED (0 to 100).    | Integer |
| `rgb`    | The brightness values of the three LEDs (0 to 100). | Tuple   |

## Motor

Generic single-direction motor.

### Wiring

...

### Code

Ensure the `Motor` class is imported at the top of the file:

```python
from gpiozero import Motor
```

Create a `Motor` object by passing in the pin number the motor is connected to:

```python
motor = Motor(4)
```

### Methods

| Method | Description | Arguments |
| ------ | ----------- | --------- |
| `on()` | Turn the motor on. | None |
| `off()` | Turn the motor off. | None |

### Properties

| Property | Description | Type |
| -------- | ----------- | ---- |
| `pin`    | The GPIO pin number the motor is connected to. | Integer |
| `is_active` | The current state of the pin (`True` if on; `False` if off). | Boolean |

# Output Devices

These output device component interfaces have been provided for simple use of
everyday components.

Components must be wired up correctly before used in code.

*Note all GPIO pin numbers use BCM numbering. See the [notes](notes.md) page
for more information.*

## LED

An LED (Light emitting diode) component.

### Wiring

Connect the cathode (the short leg) of the LED to a ground pin, and connect the
anode (the longer leg) to any GPIO pin, with a current limiting resistor in
between:

![LED wiring](images/led.png)

*Altenatively, use a breadboard to wire up the LED in the same way*

### Code

Ensure the `LED` class is imported at the top of the file:

```python
from gpiozero import LED
```

Create an `LED` object by passing in the pin number the LED is connected to:

```python
led = LED(17)
```

#### Initialisation options

```python
LED(pin=None, active_high=True)
```

| Argument | Description | Values | Default |
| -------- | ----------- | ------ | ------- |
| `pin`         | The GPIO pin number the LED is connected to.  | Integer | *Required* |
| `active_high` | Whether high or low voltage turns the LED on. | Boolean | `True`     |

#### Methods

| Method | Description | Arguments |
| ------ | ----------- | --------- |
| `on()`     | Turn the LED on.  | None |
| `off()`    | Turn the LED off. | None |
| `toggle()` | Toggle the LED. If it's on, turn it off; if it's off, turn it on. | None |
| `blink()`  | Make the LED turn on and off repeatedly. | `on_time` - The amount of time (in seconds) for the LED to be on each iteration. **Default: `1`** |
|            |                                          | `off_time` - The amount of time (in seconds) for the LED to be off each iteration. **Default: `1`** |
|            |                                          | `n` - The number of iterations. `None` means infinite. **Default: `None`** |
|            |                                          | `background` - If `True`, start a background thread to continue blinking and return immediately. If `False`, only return when the blink is finished (warning: the default value of n will result in this method never returning). **Default: `True`** |

#### Properties

| Property | Description | Type |
| -------- | ----------- | ---- |
| `pin`    | The GPIO pin number the LED is connected to.                       | Integer             |
| `is_lit` | The current state of the LED (`True` if on; `False` if off).       | Boolean             |
| `value`  | The current state of the LED (`True` if on; `False` if off).       | Boolean             |
| `values` | A generator continuously yielding the LED's current value.         | Generator           |
| `source` | A generator which can be used to continuously set the LED's value. | `None` or Generator |

## PWMLED

An LED (Light emitting diode) component with the ability to set brightness.

*Note this interface does not require a special LED component. Any regular LED
can be used in this way.*

### Wiring

A PWMLED is wired the same as a regular LED.

### Code

Ensure the `PWMLED` class is imported at the top of the file:

```python
from gpiozero import PWMLED
```

Create an `LED` object by passing in the pin number the LED is connected to:

```python
led = PWMLED(17)
```

#### Initialisation options

```python
PWMLED(pin=None, active_high=True)
```

| Argument | Description | Values | Default |
| -------- | ----------- | ------ | ------- |
| `pin`         | The GPIO pin number the LED is connected to.  | Integer | *Required* |
| `active_high` | Whether high or low voltage turns the LED on. | Boolean | `True`     |

#### Methods

| Method | Description | Arguments |
| ------ | ----------- | --------- |
| `on()`     | Turn the LED on.  | None |
| `off()`    | Turn the LED off. | None |
| `toggle()` | Toggle the LED. If it's on, turn it off; if it's off, turn it on. | None |
| `blink()`  | Make the LED turn on and off repeatedly. | `on_time` - The amount of time (in seconds) for the LED to be on each iteration. **Default: `1`** |
|            |                                          | `off_time` - The amount of time (in seconds) for the LED to be off each iteration. **Default: `1`** |
|            |                                          | `n` - The number of iterations. `None` means infinite. **Default: `None`** |
|            |                                          | `background` - If `True`, start a background thread to continue blinking and return immediately. If `False`, only return when the blink is finished (warning: the default value of n will result in this method never returning). **Default: `True`** |

#### Properties

| Property | Description | Type |
| -------- | ----------- | ---- |
| `pin`    | The GPIO pin number the LED is connected to.                       | Integer             |
| `is_lit` | The current state of the LED (`True` if on; `False` if off).       | Boolean             |
| `value`  | The current brightness of the LED `0` to `1`.                      | Float               |
| `values` | A generator continuously yielding the LED's current value.         | Generator           |
| `source` | A generator which can be used to continuously set the LED's value. | `None` or Generator |

## Buzzer

A digital Buzzer component.

### Wiring

Connect the negative pin of the buzzer to a ground pin, and connect the
positive side to any GPIO pin:

...

### Code

Ensure the `Buzzer` class is imported at the top of the file:

```python
from gpiozero import Buzzer
```

Create a `Buzzer` object by passing in the pin number the buzzer is connected
to:

```python
buzzer = Buzzer(3)
```

#### Initialisation options

```python
Buzzer(pin=None, active_high=True)
```

| Argument | Description | Values | Default |
| -------- | ----------- | ------ | ------- |
| `pin`         | The GPIO pin number the buzzer is connected to.  | Integer | *Required* |
| `active_high` | Whether high or low voltage turns the buzzer on. | Boolean | `True`     |

#### Methods

| Method | Description | Arguments |
| ------ | ----------- | --------- |
| `on()`     | Turn the buzzer on.  | None |
| `off()`    | Turn the buzzer off. | None |
| `toggle()` | Toggle the buzzer. If it's on, turn it off; if it's off, turn it on. | None |
| `beep()`   | Make the buzzer turn on and off repeatedly. | `on_time` - The amount of time (in seconds) for the buzzer to be on each iteration. **Default: `1`** |
|            |                                             | `off_time` - The amount of time (in seconds) for the buzzer to be off each iteration. **Default: `1`** |
|            |                                             | `n` - The number of iterations. `None` means infinite. **Default: `None`** |
|            |                                             | `background` - If `True`, start a background thread to continue beeping and return immediately. If `False`, only return when the blink is finished (warning: the default value of n will result in this method never returning). **Default: `True`** |

#### Properties

| Property | Description | Type |
| -------- | ----------- | ---- |
| `pin`       | The GPIO pin number the buzzer is connected to.                       | Integer             |
| `is_active` | The current state of the buzzer (`True` if on; `False` if off).       | Boolean             |
| `value`     | The current state of the buzzer (`True` if on; `False` if off).       | Boolean             |
| `values`    | A generator continuously yielding the buzzer's current value.         | Generator           |
| `source`    | A generator which can be used to continuously set the buzzer's value. | `None` or Generator |

## RGB LED

A full colour LED component (made up of Red, Green and Blue LEDs).

### Wiring

Connect the common cathode (the longest leg) to a ground pin; connect each of
the other legs (representing the red, green and blue components of the LED) to
any GPIO pins, each with a current limiting resistor in between:

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

#### Initialisation options

```python
RGBLED(red=None, green=None, blue=None)
```

| Argument | Description | Values | Default |
| -------- | ----------- | ------ | ------- |
| `red`   | The GPIO pin number the red LED is connected to.   | Integer | *Required* |
| `green` | The GPIO pin number the green LED is connected to. | Integer | *Required* |
| `blue`  | The GPIO pin number the blue LED is connected to.  | Integer | *Required* |

#### Methods

| Method | Description | Arguments |
| ------ | ----------- | --------- |
| `on()`     | Turn all the LEDs on (makes white light). | None |
| `off()`    | Turn all the LEDs off.                    | None |
| `toggle()` | Toggle the LED. If it's on (at all), turn it off; if it's off, turn it on. | None |
| `blink()`  | Make the LED turn on and off repeatedly. | `on_time` - The amount of time (in seconds) for the LED to be on each iteration. **Default: `1`** |
|            |                                          | `off_time` - The amount of time (in seconds) for the LED to be off each iteration. **Default: `1`** |
|            |                                          | `n` - The number of iterations. `None` means infinite. **Default: `None`** |
|            |                                          | `background` - If `True`, start a background thread to continue blinking and return immediately. If `False`, only return when the blink is finished (warning: the default value of n will result in this method never returning). **Default: `True`** |

#### Properties

| Property | Description | Type |
| -------- | ----------- | ---- |
| `red`    | The brightness value of the red LED (`0` to `1`).                     | Float               |
| `green`  | The brightness value of the green LED (`0` to `1`).                   | Float               |
| `blue`   | The brightness value of the blue LED (`0` to `1`).                    | Float               |
| `color`  | The brightness values of the three LEDs `(0, 0, 0)` to `(1, 1, 1)`.   | Tuple               |
| `value`  | The brightness values of the three LEDs `(0, 0, 0)` to `(1, 1, 1)`.   | Tuple               |
| `values` | A generator continuously yielding the LED's current values.           | Generator           |
| `source` | A generator which can be used to continuously set the LED's values.   | `None` or Generator |

## Motor

Generic bi-directional motor.

### Wiring

Attach a Motor Controller Board to your Pi, connect a battery pack to the Motor
Controller Board, and connect each side of the motor to any GPIO pin:

...

### Code

Ensure the `Motor` class is imported at the top of the file:

```python
from gpiozero import Motor
```

Create a `Motor` object by passing in the pin numbers the motor is connected to:

```python
motor = Motor(forward=17, backward=18)
```

#### Initialisation options

```python
Motor(forward=None, backward=None)
```

| Argument | Description | Values | Default |
| -------- | ----------- | ------ | ------- |
| `forward`     | The GPIO pin number the forward gear of the motor is connected to. | Integer | *Required* |
| `backward`    | The GPIO pin number the reverse gear of the motor is connected to. | Integer | *Required* |

#### Methods

| Method | Description | Arguments |
| ------ | ----------- | --------- |
| `forward()`  | Drive the motor forwards.       | `speed` - Speed at which to drive the motor, `0` to `1`. **Default: `1`** |
| `backward()` | Drive the motor backwards.      | `speed` - Speed at which to drive the motor, `0` to `1`. **Default: `1`** |
| `stop()`     | Stop the motor.                 | None |
| `reverse()`  | Reverse direction of the motor. | None |

#### Properties

| Property | Description | Type |
| -------- | ----------- | ---- |
| `is_active` | The current state of the motor. `True` if moving, otherwise `False`.                                                      | Boolean             |
| `value`     | The current speed and direction of the motor. `-1.0` if full speed backward, `0.0` if still, `1.0` if full speed forward. | Float               |
| `values`    | A generator continuously yielding the motor's current value.                                                              | Generator           |
| `source`    | A generator which can be used to continuously set the motor's value.                                                      | `None` or Generator |

## LEDBargraph

A strip of seperate LEDs in a single component.

### Wiring

The LED bargraph component has 2 rows of pins, a row of cathodes and a row of
anodes, one pair for each LED in the bargraph.

Connect the cathode of each LED to a ground pin, and connect the
anode (the longer leg) to any GPIO pin, with a current limiting resistor in
between:

### Code

Ensure the `LEDBargraph` class is imported at the top of the file:

```python
from gpiozero import LEDBargraph
```

Create an `LEDBargraph` object by passing in a tuple of the GPIO pins
each LED is connected too. 

```python
bar = LEDBargraph((24, 25, 10, 9, 11, 8, 7, 5, 6, 12))
```

#### Initialisation options

```python
LED(led_pins)
```

| Argument | Description | Values | Default |
| -------- | ----------- | ------ | ------- |
| `led_pins` | A tuple of gpio pins  | Tuple | Required |

#### Methods

| Method | Description | Arguments |
| ------ | ----------- | --------- |
| `on()`     | Turn the LED bargraph on.  | `*args` - position of led(s) to turn on *optional*  |
| `off()`     | Turn the LED bargraph off.  | `*args` - position of led(s) to turn off *optional*  |
| `on_up_to()`     | Turn all the LEDs on up to a position.  | `led_no` - position of led to turn on the leds up to |
| `on_down_to()`     | Turn all the LEDs on down to a position.  | `led_no` - position of led to turn on the leds down to |
| `led()`     | The LED object reference of the led at a position  | `led_no` - position of led |
| `close()`     | Close the LED bargraph  | None |

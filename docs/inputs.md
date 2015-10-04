# Input Devices

These input device component interfaces have been provided for simple use of
everyday components.

Components must be wired up correctly before used in code.

*Note all GPIO pin numbers use BCM numbering. See the [notes](notes.md) page
for more information.*

## Button

A physical push button or switch.

### Wiring

...

### Code

Ensure the `Button` class is imported at the top of the file:

```python
from gpiozero import Button
```

Create a `Button` object by passing in the pin number the button is connected
to:

```python
button = Button(2)
```

The default behaviour is to set the *pull* state of the button to *up*. To
change this behaviour, set the `pull_up` argument to `False` when creating your
`Button` object.

```python
button = Button(pin=2, pull_up=False)
```

### Methods

| Method | Description | Arguments |
| ------ | ----------- | --------- |
| `wait_for_press()` | Halt the program until the button is pressed. | `timeout` - The number of seconds to wait before proceeding if no event is detected. Default: `None` |
| `wait_for_release()` | Halt the program until the button is released. | `timeout` - The number of seconds to wait before proceeding if no event is detected. Default: `None`  |

### Properties

| Property | Description | Type |
| -------- | ----------- | ---- |
| `pin`    | The GPIO pin number the button is connected to. | Integer |
| `is_pressed` | The current state of the pin (`True` if pressed; otherwise `False`). | Boolean |
| `pull_up` | The pull state of the pin (`True` if pulled up; `False` if pulled down). | Boolean |
| `when_pressed` | A reference to the function to be called when the button is pressed. | None or Function |
| `when_released` | A reference to the function to be called when the button is released. | None or Function |

## Motion Sensor

A PIR (Passive Infra-Red) motion sensor.

### Wiring

...

### Code

Ensure the `MotionSensor` class is imported at the top of the file:

```python
from gpiozero import MotionSensor
```

Create a `MotionSensor` object by passing in the pin number the sensor is
connected to:

```python
pir = MotionSensor(3)
```

### Methods

...

### Properties

...

## Light Sensor

An LDR (Light Dependent Resistor) Light Sensor.

### Wiring

...

### Code

Ensure the `LightSensor` class is imported at the top of the file:

```python
from gpiozero import LightSensor
```

Create a `LightSensor` object by passing in the pin number the sensor is
connected to:

```python
light = LightSensor(4)
```

### Methods

...

### Properties

...

## Temperature Sensor

Digital Temperature Sensor.

### Wiring

...

### Code

Ensure the `TemperatureSensor` class is imported at the top of the file:

```python
from gpiozero import TemperatureSensor
```

Create a `TemperatureSensor` object:

```python
temp = TemperatureSensor()
```

### Properties

...

### Methods

...

## MCP3008 Analogue-to-Digital Converter

MCP3008 ADC (Analogue-to-Digital converter).

The MCP3008 chip provides access to up to 8 analogue inputs, such as
potentiometers, and read their values in digital form.

### Wiring

...

### Code

Ensure the `MCP3008` class is imported at the top of the file:

```python
from gpiozero import MCP3008
```

Access an input value with the `MCP3008`'s context manager:

```python
with MCP3008() as pot:
    print(pot.read())
```

It is possible to specify the `bus`, the `device` and the `channel` you wish to
access. The previous example used the default value of `0` for each of these.
To specify them, pass them in as arguments:

```python
with MCP3008(bus=1, device=1, channel=4) as pot:
    print(pot.read())
```

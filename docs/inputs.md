# Input Devices

These input device component interfaces have been provided for simple use of
everyday components.

Components must be wired up correctly before used in code.

*Note all GPIO pin numbers use BCM numbering. See the [notes](notes.md) page
for more information.*

## Button

A physical push button or switch.

### Wiring

Connect one side of the button to a ground pin, and the other to any GPIO pin:

![GPIO Button wiring](images/button.png)

*Alternatively, connect to 3V3 and to a GPIO, and set `pull_up` to `False` when
you create your `Button` object.*

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

#### Initialisation options

```python
Button(pin=None, pull_up=True, bounce_time=None)
```

| Argument | Description | Values | Default |
| -------- | ----------- | ------ | ------- |
| `pin`         | The GPIO pin number the button is connected to. | Integer: `0` to `25` | *Required* |
| `pull_up`     | The pull state of the pin. `True` means pull up, `False` means pull down. | Boolean | `True` |
| `bounce_time` | Specifies the length of time (in seconds) that the component will ignore changes in state after an initial change. | Integer or Float | `None` |

#### Methods

| Method | Description | Arguments |
| ------ | ----------- | --------- |
| `wait_for_press()`   | Halt the program until the button is pressed.  | `timeout` - The number of seconds to wait before proceeding if no event is detected. **Default: `None`** |
| `wait_for_release()` | Halt the program until the button is released. | `timeout` - The number of seconds to wait before proceeding if no event is detected. **Default: `None`** |

#### Properties

| Property | Description | Type |
| -------- | ----------- | ---- |
| `pin`           | The GPIO pin number the button is connected to.                          | Integer            |
| `is_pressed`    | The current state of the pin (`True` if pressed; otherwise `False`).     | Boolean            |
| `pull_up`       | The pull state of the pin (`True` if pulled up; `False` if pulled down). | Boolean            |
| `when_pressed`  | A reference to the function to be called when the button is pressed.     | `None` or Function |
| `when_released` | A reference to the function to be called when the button is released.    | `None` or Function |

## Motion Sensor

A PIR (Passive Infra-Red) motion sensor.

### Wiring

Connect the pin labelled `VCC` to a 5V pin; connect the one labelled `GND` to
a ground pin; and connect the one labelled `OUT` to any GPIO pin:

![Motion Sensor wiring](images/motion-sensor.png)

### Code

Ensure the `MotionSensor` class is imported at the top of the file:

```python
from gpiozero import MotionSensor
```

Create a `MotionSensor` object by passing in the pin number the sensor is
connected to:

```python
pir = MotionSensor(4)
```

#### Initialisation options

```python
MotionSensor(pin=None, queue_len=1, sample_rate=10, threshold=0.5, partial=False)
```

| Argument | Description | Values | Default |
| -------- | ----------- | ------ | ------- |
| `pin`         | The GPIO pin number the sensor is connected to. | Integer: `0` to `25` | *Required* |
| `queue_len`   | ??? | Integer | `1` |
| `sample_rate` | ??? | Integer | `10` |
| `threshold`   | Proportion of sensor values required to determine motion state. | Float: `0` to `1` | `0.5` |
| `partial`     | ??? | Boolean | `False` |

#### Methods

| Method | Description | Arguments |
| ------ | ----------- | --------- |
| `wait_for_motion()`    | Halt the program until motion is detected.    | `timeout` - The number of seconds to wait before proceeding if no motion is detected. **Default: `None`**    |
| `wait_for_no_motion()` | Halt the program until no motion is detected. | `timeout` - The number of seconds to wait before proceeding if motion is still detected. **Default: `None`** |

#### Properties

| Property | Description | Type |
| -------- | ----------- | ---- |
| `pin`    | The GPIO pin number the sensor is connected to. | Integer |
| `motion_detected` | The current state of the sensor (`True` if motion is detected; otherwise `False`). | Boolean |
| `when_motion` | A reference to the function to be called when motion is detected. | `None` or Function |
| `when_no_motion` | A reference to the function to be called when no motion is detected. | `None` or Function |

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

#### Initialisation options

```python
LightSensor(pin=None, queue_len=5, charge_time_limit=10,
    threshold=0.1, partial=False)
```

| Argument | Description | Values | Default |
| -------- | ----------- | ------ | ------- |
| `pin`         | The GPIO pin number the sensor is connected to. | Integer: `0` to `25` | *Required* |
| `queue_len`   | ??? | Integer | `5` |
| `charge_time_limit` | Maximum amount of time allowed to determine darkness. | Integer | `10` |
| `threshold`   | Proportion of sensor values required to determine light level. | Float: `0` to `1` | `0.1` |
| `partial`     | ??? | Boolean | `False` |

#### Methods

| Method | Description | Arguments |
| ------ | ----------- | --------- |
| `wait_for_light()` | Halt the program until light is detected.    | `timeout` - The number of seconds to wait before proceeding if light is not detected. **Default: `None`** |
| `wait_for_dark()`  | Halt the program until darkness is detected. | `timeout` - The number of seconds to wait before proceeding if darkness is not detected. **Default: `None`** |

#### Properties

| Property | Description | Type |
| -------- | ----------- | ---- |
| `pin`            | The GPIO pin number the sensor is connected to.                       | Integer            |
| `light_detected` | The current state of the sensor (`True` if light; otherwise `False`). | Boolean            |
| `when_light`     | A reference to the function to be called when light is detected.      | `None` or Function |
| `when_dark`      | A reference to the function to be called when darkness is detected.   | `None` or Function |

## Temperature Sensor

One-wire Digital Temperature Sensor.

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

#### Initialisation options

...

#### Methods

...

#### Properties

| Property | Description | Type |
| -------- | ----------- | ---- |
| `value`  | The current temperature reading in degrees Celsius. | Float |

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

Create an `MCP3008` object:

```python
pot = MCP3008()
```

Alternatively, access an input value with the `MCP3008`'s context manager:

```python
with MCP3008() as pot:
    # do something with pot
```

#### Initialisation options

```python
MCP3008(device=0, channel=0)
```

| Argument | Description | Values | Default |
| -------- | ----------- | ------ | ------- |
| `device`  | Which of the two Chip Select SPI pins to access. | Integer: `0` or `1` | `0` |
| `channel` | Which of the 8 ADC channels to access.           | Integer: `0` to `7` | `0` |

#### Methods

| Method | Description | Arguments |
| ------ | ----------- | --------- |
| `wait_for_light()` | Halt the program until light is detected.    | `timeout` - The number of seconds to wait before proceeding if light is not detected. **Default: `None`** |
| `wait_for_dark()`  | Halt the program until darkness is detected. | `timeout` - The number of seconds to wait before proceeding if darkness is not detected. **Default: `None`** |

#### Properties

| Property | Description | Type |
| -------- | ----------- | ---- |
| `pin`            | The GPIO pin number the sensor is connected to.                       | Integer            |
| `light_detected` | The current state of the sensor (`True` if light; otherwise `False`). | Boolean            |
| `when_light`     | A reference to the function to be called when light is detected.      | `None` or Function |
| `when_dark`      | A reference to the function to be called when darkness is detected.   | `None` or Function |

## MCP3004 Analogue-to-Digital Converter

MCP3004 ADC (Analogue-to-Digital converter).

The MCP3004 chip provides access to up to 4 analogue inputs, such as
potentiometers, and read their values in digital form.

The interface is identical to `MCP3008`, except that only channels `0` to `3`
are accessible.

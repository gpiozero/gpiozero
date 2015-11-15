# Notes

## BCM pin numbering

This library uses Broadcom (BCM) pin numbering for the GPIO pins, as
opposed to BOARD. Unlike the `RPi.GPIO` library, this is not configurable.

Any pin marked `GPIO` can be used for generic components.

The BCM pin layout is as follows:

|            |            |
|-----------:|:-----------|
|    3V3     | 5V         |
|  **GPIO2** | 5V         |
|  **GPIO3** | GND        |
|  **GPIO4** | **GPIO14** |
|        GND | **GPIO15** |
| **GPIO17** | **GPIO18** |
| **GPIO27** | GND        |
| **GPIO22** | **GPIO23** |
|        3V3 | **GPIO24** |
| **GPIO10** | GND        |
|  **GPIO9** | **GPIO25** |
| **GPIO11** | **GPIO8**  |
|        GND | **GPIO7**  |
|        DNC | DNC        |
|  **GPIO5** | GND        |
|  **GPIO6** | **GPIO12** |
| **GPIO13** | GND        |
| **GPIO19** | **GPIO16** |
| **GPIO26** | **GPIO20** |
|        GND | **GPIO21** |

- *GND = Ground*
- *3V3 = 3.3 Volts*
- *5V = 5 Volts*
- *DNC = Do not connect (special use pins)*

## Wiring

All components must be wired up correctly before using with this library.

## Keep your program alive with `signal.pause`

The following program looks like it should turn an LED on:

```python
from gpiozero import led

led = LED(2)
led.on()
```

And it does, if you're using the Python shell, IPython shell or IDLE shell,
but if you saved this program as a Python file and ran it, it would flash
on for a moment then the program would end and it would turn off.

The following file includes an intentional `pause` to keep the program
alive:

```python
from gpiozero import LED
from signal import pause

led = LED(2)
led.on()
pause()
```

Now running the program will stay running, leaving the LED on, until it is
forced to quit.

Similarly, when setting up callbacks on button presses or other input
devices, the program needs to be running for the events to be detected:

```python
from gpiozero import Button
from signal import pause

def hello():
    print("Hello")

button = Button(2)
button.when_pressed = hello
pause()
```

## Importing from GPIO Zero

In Python, libraries and functions used in a script must be imported by name at
the top of the file, with the exception of the functions built in to Python by
default.

For example, to use the `Button` interface from the GPIO Zero library, it
should be explicitly imported:

```python
from gpiozero import Button
```

Now `Button` is available directly in the script:

```python
button = Button(2)
```

Alternatively, the whole GPIO Zero library can be imported:

```python
import gpiozero
```

In this case, all references to interfaces within GPIO Zero must be prefixed:

```python
button = gpiozero.Button(2)
```

## Programming terms

The following terms are used in the documentation.

### Class

A class is the blueprint for a data type. A class defines the way an instance
of its own can behave, and has specific functionality relating to the kinds of
things a user would expect to be able to do with it.

An example of a class in GPIO Zero is `Button`. Note class names are given with
each word capitalised.

### Object

An object is an instance of a class. Any variable in Python is an object of a
given type (e.g. Integer, String, Float), and comprises the functionality
defined by its class.

To create an object, you must assign a variable name to an instance of a class:

```python
my_button = Button(2)
```

Now the variable `my_button` is an instance of the class `Button`. Check its
type with Python's `type()` function:

```python
print(type(my_button))
```

which shows:

```
gpiozero.Button
```

### Initialisation options

Most classes in GPIO Zero require some arguments to create an object, for
example the `LED` and `Button` examples require the pin number the device is
attached to:

```python
my_button = Button(2)
```

Some classes have multiple arguments, usually with some being optional. When
arguments are optional, common default values are used. The following example:

```python
my_button = Button(2)
```

is equivalent to:

```python
my_button = Button(2, True)
```

because the second argument defaults to `True`.

Arguments can be given unnamed, as long as they are in order:

```python
my_button = Button(2, False)
```

though this may be confusing, so named is better in this case:

```python
my_button = Button(pin=2, pull_up=False)
```

Alternatively, they can be given in any order, as long as they are named:

```python
my_button = Button(pin=2, bounce_time=0.5, pull_up=False)
```

### Method

A method is a function defined within a class. With an object of a given type,
you can call a method on that object. For example if `my_led` is a `LED`
object:

```python
my_led.on()
```

will call the `LED` class's `on()` function, relating to that instance of
`LED`. If other `LED` objects have been created, they will not be affected by
this action.

In many cases, no arguments are required to call the method (like
`my_led.on()`). In other cases, optional arguments are available. For example:

```python
my_led.blink(2, 3)
```

Here, the arguments `2` and `3` have been passed in as arguments. The `blink`
method allows configuration of `on_time` and `off_time`. This example means the
LED will flash on for 2 seconds and stay off for 3. This example may benefit
from use of named arguments:

```python
my_led.blink(on_time=2, off_time=3)
```

arguments can also be passed in by name, which means order is irrelevant. For
example:

```python
my_led.blink(off_time=3)
```

Here, only the `off_time` argument has been provided, and all other arguments
will use their default values. Methods in GPIO Zero use sensible common default
values, but are configurable when necessary.

### Property

A property is an attribute relating to the state of an object. For example:

```python
my_led.is_lit
```

This will return `True` or `False` depending on whether or not the LED is
currently lit.

Some properties allow you to change their value. For example an `RGBLED` object:

```python
rgb_led.green = 0.5
```

or:

```python
rgb_led.color = (0.2, 0.3, 0.7)
```

### Context manager

A context manager is an alternative interface provided by classes which require
"closing" the object when it's finished with. The following example (using a
context manager):

```python
with MCP3008() as pot:
    print(pot.value)
```

is identical to:

```python
pot = MCP3008()
print(pot.value)
pot.close()
```

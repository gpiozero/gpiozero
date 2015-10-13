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

button = Button(2)
button.when_pressed = lambda: print("Button was pressed!")
pause()
```

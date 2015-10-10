# GPIO Zero

A simple interface to everyday GPIO components used with Raspberry Pi.

Created by [Ben Nuttall](https://github.com/bennuttall) of the [Raspberry Pi
Foundation](https://www.raspberrypi.org/), [Dave
Jones](https://github.com/waveform80), and other contributors.

## Latest release

The latest release is **v0.7.0 beta 2** released on 9th October 2015.

## About

With very little code, you can quickly get going connecting your physical
components together:

    from gpiozero import LED, Button

    led = LED(2)
    button = Button(3)

    button.when_pressed = led.on
    button.when_released = led.off

The library includes interfaces to many simple everyday components, as well as
some more complex things like sensors, analogue-to-digital converters, full
colour LEDs, robotics kits and more.

## Install

Install with pip:

```bash
sudo apt-get install python-pip python3-pip
sudo pip install gpiozero
sudo pip-3.2 install gpiozero
```

Both Python 3 and Python 2 are supported. Python 3 is recommended!

### Upgrade

Upgrade to the latest version with:

```bash
sudo pip install gpiozero --upgrade
sudo pip-3.2 install gpiozero --upgrade
```

## Getting started

See the [input devices](inputs.md) and [output devices](outputs.md) to get
started. Also see the [boards & accessories](boards.md) page for examples of
using the included accessories.

For common programs using multiple components together, see the
[recipes](recipes.md) page.

## Development

This project is being developed on
[GitHub](https://github.com/RPi-Distro/python-gpiozero). Join in:

* Provide suggestions, report bugs and ask questions as
[Issues](https://github.com/RPi-Distro/python-gpiozero/issues)
* Provide examples we can use as
[recipes](http://pythonhosted.org/gpiozero/recipes/)
* Contribute to the code

Alternatively, email suggestions and feedback to ben@raspberrypi.org or add to
the [Google Doc](https://goo.gl/8zJLif).

## Contributors

- [Ben Nuttall](https://github.com/bennuttall) (project maintainer)
- [Dave Jones](https://github.com/waveform80)
- [Martin O'Hanlon](https://github.com/martinohanlon)

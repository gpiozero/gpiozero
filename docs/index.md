# GPIO Zero

A simple interface to everyday GPIO components used with Raspberry Pi

## Latest release

The latest release is **v0.6.0 beta 1** released on 28th September 2015.

## Motivation

The "hello world" program in Java is at least 5 lines long, and contains 11
jargon words which are to be ignored. The "hello world" program in Python is
one simple line. However, the "hello world" of physical computing in Python
(flashing an LED) is similar to the Java program.

6 lines of code to flash an LED. And skipping over why `GPIO` is used twice in
the first line; what `BCM` means; why set warnings to False; and so on. Young
children and beginners shouldn't need to sit and copy out several lines of text
they're told to ignore. They should be able to read their code and understand
what it means. This module provides a simple interface to everyday components.
The LED example becomes:

```python
from gpiozero import LED

red = LED(2)

red.on()
```

Any guesses how to turn it off?

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

## What's included?

Components:

- LED
- Buzzer
- Button
- Motion Sensor
- Light Sensor
- Temperature Sensor
- Motor

Boards & accessories:

- LED Board
- Traffic Lights
- PiLITEr
- PI-TRAFFIC
- Fish Dish
- Traffic HAT

## Getting started

See the [input devices](inputs.md) and [output devices](outputs.md) to get started. Also see the [boards & accessories](boards.md) page for examples of using the included accessories.

For common programs using multiple components together, see the [recipes](recipes.md) page.

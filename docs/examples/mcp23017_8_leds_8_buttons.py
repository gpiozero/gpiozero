from gpiozero import LED, Button, MCP23017Factory
from signal import pause

factory = MCP23017Factory()
buttons = [Button(i, pin_factory=factory) for i in range(8)]
leds = [LED(i, pin_factory=factory) for i in range(8, 16)]

for i in range(8):
    # When a button is pressed, turn the associated LED on
    # (i.e. when the GPA0 button is pressed, GPB0 LED is turned on)
    button[i].when_pressed = leds[i + 8].on
    # When it is released, turn off its LED
    button[i].when_released = leds[i + 8].off

pause()

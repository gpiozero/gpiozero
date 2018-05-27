from gpiozero import LED, Button, MCP23017Factory
from signal import pause

factory = MCP23017Factory()
led = LED(7, pin_factory=factory)
button = Button(8, pin_factory=factory)

led.source = button.values

pause()

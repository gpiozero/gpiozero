from gpiozero import RGBLED, MCP3008
from signal import pause

led = RGBLED(2, 3, 4)
red_pot = MCP3008(0)
green_pot = MCP3008(1)
blue_pot = MCP3008(2)

led.source = zip(red_pot.values, green_pot.values, blue_pot.values)

pause()

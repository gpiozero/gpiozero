from gpiozero import LEDBoard
from time import sleep

leds = LEDBoard(red=LEDBoard(top=2, bottom=3), green=LEDBoard(top=4, bottom=5))

leds.red.on() ## both reds on
sleep(1)
leds.green.on()  # both greens on
sleep(1)
leds.off()  # all off
sleep(1)
leds.red.top.on()  # top red on
sleep(1)
leds.green.bottom.on()  # bottom green on
sleep(1)

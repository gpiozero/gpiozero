from gpiozero import LEDBoard
from time import sleep

leds = LEDBoard(2, 3, 4, 5, 6, 7, 8, 9)

for led in leds[3:]:  # leds 3 and onward
    led.on()
sleep(1)
leds.off()

for led in leds[:2]:  # leds 0 and 1
    led.on()
sleep(1)
leds.off()

for led in leds[::2]:  # even leds (0, 2, 4...)
    led.on()
sleep(1)
leds.off()

for led in leds[1::2]:  # odd leds (1, 3, 5...)
    led.on()
sleep(1)
leds.off()

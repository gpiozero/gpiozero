from gpiozero import Button, LED
from signal import pause

def opposite(values):
    for value in values:
        yield not value

led = LED(4)
btn = Button(17)

led.source = opposite(btn.values)

pause()

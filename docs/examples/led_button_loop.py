from gpiozero import LED, Button
from time import sleep

led = LED(17)
button = Button(2)

while True:
    led.value = button.value
    sleep(0.01)

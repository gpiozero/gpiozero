from gpiozero import LED, Button

led = LED(17)
button = Button(2)

while True:
    led.value = button.value

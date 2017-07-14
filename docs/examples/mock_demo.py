from gpiozero.pins.mock import MockFactory
from gpiozero import Device, Button, LED
from time import sleep

# Set the default pin factory to a mock factory
Device.pin_factory = MockFactory()

# Construct a couple of devices attached to mock pins 16 and 17, and link the
# devices
led = LED(17)
btn = Button(16)
led.source = btn.values

# Here the button isn't "pushed" so the LED's value should be False
print(led.value)

# Get a reference to mock pin 16 (used by the button)
btn_pin = Device.pin_factory.pin(16)

# Drive the pin low (this is what would happen eletrically when the button is
# pushed)
btn_pin.drive_low()
sleep(0.1) # give source some time to re-read the button state
print(led.value)

btn_pin.drive_high()
sleep(0.1)
print(led.value)

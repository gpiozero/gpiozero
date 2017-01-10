from gpiozero import Buzzer, Button
from gpiozero.pins.pigpio import PiGPIOPin
from signal import pause

ips = ['192.168.1.3', '192.168.1.4', '192.168.1.5', '192.168.1.6']
remote_pins = [PiGPIOPin(17, host=ip) for ip in ips]

button = Button(17)  # button on this pi
buzzers = [Buzzer(pin) for pin in remote_pins]  # buzzers on remote pins

for buzzer in buzzers:
    buzzer.source = button.values

pause()

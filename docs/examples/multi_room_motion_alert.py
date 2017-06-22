from gpiozero import LEDBoard, MotionSensor
from gpiozero.pins.pigpio import PiGPIOPin
from signal import pause

ips = ['192.168.1.3', '192.168.1.4', '192.168.1.5', '192.168.1.6']
remote_pins = [PiGPIOPin(17, host=ip) for ip in ips]

leds = LEDBoard(2, 3, 4, 5)  # leds on this pi
sensors = [MotionSensor(pin) for pin in remote_pins]  # motion sensors on other pis

for led, sensor in zip(leds, sensors):
    led.source = sensor.values

pause()

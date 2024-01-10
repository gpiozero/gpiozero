from gpiozero import Button
from picamera import PiCamera
from datetime import datetime
from signal import pause

button = Button(2)
camera = PiCamera()

def capture():
    camera.capture(f'/home/pi/{datetime.now():%Y-%m-%d-%H-%M-%S}.jpg')

button.when_pressed = capture

pause()

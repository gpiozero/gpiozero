from gpiozero import Button
from picamera import PiCamera
from datetime import datetime
from signal import pause

button = Button(2)
camera = PiCamera()

def capture():
    timestamp = datetime.now().isoformat()
    camera.capture('/home/pi/{timestamp}.jpg'.format(timestamp=timestamp))

button.when_pressed = capture

pause()

from RPi import GPIO


class OutputDevice(object):
    def __init__(self, pin):
        self.pin = pin
        GPIO.setup(pin, GPIO.OUT)

    def on(self):
        GPIO.output(self.pin, True)

    def off(self):
        GPIO.output(self.pin, False)


class LED(OutputDevice):
    pass


class Buzzer(OutputDevice):
    pass


class Motor(OutputDevice):
    pass

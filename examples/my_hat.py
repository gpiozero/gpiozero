from gpio_components import LED, Buzzer, Button
from time import sleep


class MyHat(object):
    def __init__(self):
        self.red = LED(9)
        self.yellow = LED(10)
        self.green = LED(11)
        self.buzzer = Buzzer(14)
        self.button = Button(15)

        self.leds = [self.red, self.yellow, self.green]
        self.outputs = self.leds + [self.buzzer]

    def all_on(self):
        for device in self.outputs:
            device.on()

    def all_off(self):
        for device in self.outputs:
            device.off()


if __name__ == '__main__':
    hat = MyHat()

    while True:
        if hat.button.is_pressed():
            hat.all_on()
        else:
            hat.all_off()

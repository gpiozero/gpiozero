from travispy import TravisPy
from gpiozero import LED
from gpiozero.tools import negated
from time import sleep
from signal import pause

def build_passed(repo='RPi-Distro/python-gpiozero', delay=3600):
    t = TravisPy()
    r = t.repo(repo)
    while True:
        yield r.last_build_state == 'passed'
        sleep(delay) # Sleep an hour before hitting travis again

red = LED(12)
green = LED(16)

red.source = negated(green.values)
green.source = build_passed()
pause()

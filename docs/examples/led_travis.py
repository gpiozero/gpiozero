from travispy import TravisPy
from gpiozero import LED
from gpiozero.tools import negated
from time import sleep
from signal import pause

def build_passed(repo):
    t = TravisPy()
    r = t.repo(repo)
    while True:
        yield r.last_build_state == 'passed'

red = LED(12)
green = LED(16)

green.source = build_passed('gpiozero/gpiozero')
green.source_delay = 60 * 5  # check every 5 minutes
red.source = negated(green)

pause()

from gpiozero import LED, PingServer
from gpiozero.tools import negated
from signal import pause

green = LED(17)
red = LED(18)

google = PingServer('google.com')

google.when_activated = green.on
google.when_deactivated = green.off
red.source = negated(green)

pause()

from gpiozero import LED, PingServer
from gpiozero.tools import negated
from signal import pause

green = LED(17)
red = LED(18)

google = PingServer('google.com')

green.source = google
green.source_delay = 60
red.source = negated(green)

pause()

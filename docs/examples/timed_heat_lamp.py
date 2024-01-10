from gpiozero import Energenie, TimeOfDay
from datetime import time
from signal import pause

lamp = Energenie(1)
daytime = TimeOfDay(time(8), time(20))

daytime.when_activated = lamp.on
daytime.when_deactivated = lamp.off

pause()

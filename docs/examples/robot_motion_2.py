from gpiozero import Robot, MotionSensor
from gpiozero.tools import zip_values
from signal import pause

robot = Robot(left=(4, 14), right=(17, 18))
pir = MotionSensor(5)

robot.source = zip_values(pir, pir)

pause()

from gpiozero import Robot, Motor, MotionSensor
from gpiozero.tools import zip_values
from signal import pause

robot = Robot(left=Motor(4, 14), right=Motor(17, 18))
pir = MotionSensor(5)

robot.source = zip_values(pir, pir)

pause()

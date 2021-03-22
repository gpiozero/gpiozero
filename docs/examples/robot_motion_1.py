from gpiozero import Robot, Motor, MotionSensor
from signal import pause

robot = Robot(left=Motor(4, 14), right=Motor(17, 18))
pir = MotionSensor(5)

pir.when_motion = robot.forward
pir.when_no_motion = robot.stop

pause()

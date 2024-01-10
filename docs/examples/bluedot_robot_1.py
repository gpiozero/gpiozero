from bluedot import BlueDot
from gpiozero import Robot, Motor
from signal import pause

bd = BlueDot()
robot = Robot(left=Motor(4, 14), right=Motor(17, 18))

def move(pos):
    if pos.top:
        robot.forward(pos.distance)
    elif pos.bottom:
        robot.backward(pos.distance)
    elif pos.left:
        robot.left(pos.distance)
    elif pos.right:
        robot.right(pos.distance)

bd.when_pressed = move
bd.when_moved = move
bd.when_released = robot.stop

pause()

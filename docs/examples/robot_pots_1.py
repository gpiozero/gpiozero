from gpiozero import Robot, MCP3008
from signal import pause

robot = Robot(left=(4, 14), right=(17, 18))

left = MCP3008(0)
right = MCP3008(1)

robot.source = zip(left.values, right.values)

pause()

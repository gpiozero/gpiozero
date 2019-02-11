from gpiozero import Robot, MCP3008
from gpiozero.tools import scaled
from signal import pause

robot = Robot(left=(4, 14), right=(17, 18))

left_pot = MCP3008(0)
right_pot = MCP3008(1)

robot.source = zip(scaled(left_pot, -1, 1), scaled(right_pot, -1, 1))

pause()

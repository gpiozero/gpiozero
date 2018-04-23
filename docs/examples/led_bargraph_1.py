from gpiozero import LEDBarGraph
from time import sleep
from __future__ import division  # required for python 2

graph = LEDBarGraph(5, 6, 13, 19, 26, 20)

graph.value = 1  # (1, 1, 1, 1, 1, 1)
sleep(1)
graph.value = 1/2  # (1, 1, 1, 0, 0, 0)
sleep(1)
graph.value = -1/2  # (0, 0, 0, 1, 1, 1)
sleep(1)
graph.value = 1/4  # (1, 0, 0, 0, 0, 0)
sleep(1)
graph.value = -1  # (1, 1, 1, 1, 1, 1)
sleep(1)

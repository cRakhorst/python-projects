from turtle import *

i = 0
currentIndex = 0
visited_positions = set()
start_position = (0, 0)

while True:
    i += 1
    currentIndex += 1
    speed(0)
    forward(10 + 2 * i)
    right(120 + i % 2)
    if currentIndex == 500:
        i = 0
        currentIndex = 0
        visited_positions.clear()
        clearscreen()
    
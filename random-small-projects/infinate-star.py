#make a script that makes a beautiful star that has an infinite loop that resets the page when it loops

from turtle import *

i = 0
currentIndex = 0
visited_positions = set()
start_position = (0, 0)

while True:
    i += 1
    speed(0)
    forward(100)
    right(166)
    forward(200)
    pos = (round(xcor()), round(ycor()))
    if pos == start_position:
        visited_positions.clear()
        clearscreen()
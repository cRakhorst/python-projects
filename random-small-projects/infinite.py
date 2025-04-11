# make a script that checks if i / 360 is a interger and uses that in the py-turtle infinite loop
from turtle import *

viableNumbers = []

def is_whole(n):
    return n % 1 == 0

for j in range (1, 360):
    number = is_whole(360 / j)
    increment = j
    if (number):
        viableNumbers.append(increment)

print(viableNumbers)

i = 0
currentIndex = 0
visited_positions = set()
start_position = (0, 0)

while True:
    i += 1
    speed(0)
    forward(5)
    right(i ** 2 * viableNumbers[currentIndex])
    
    pos = (round(xcor()), round(ycor()))
    if pos == start_position:
        currentIndex += 1
        if currentIndex >= len(viableNumbers):
            currentIndex = 0
        visited_positions.clear()
        clearscreen()
    else:
        visited_positions.add(pos)
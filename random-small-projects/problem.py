# if the number is odd, multiply by 3 and add 1
# if the number is even, divide by 2

from turtle import *

def collatz_graph(n):
    x = -420
    y = -390

    penup()
    goto(x, y)
    pendown()

    while n != 1:
        if n % 2 == 0:
            n = n // 2 
        else:
            n = 3 * n + 1

        x += 5
        y = -390 + (n / 2) 
        goto(x, y)

speed(0)
bgcolor("black")
color("white")

highest = 0
highestStart = 1
ceiling = 100

for i in range(1, ceiling):
    n = i
    while n != 1:
        if n % 2 == 0:
            if n > highest:
                highest = int(n)
                highestStart = int(i)
                print('highest number found:', highest, 'With the starting number:', highestStart, 'Numbers left:', ceiling - i)
            n = n / 2
        else:
            n = 3 * n + 1
print('highest number found in the range 1 to', i, 'is:', highest, 'with the highest starting number:', highestStart)
collatz_graph(highestStart)

done()
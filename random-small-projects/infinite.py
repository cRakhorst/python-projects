import turtle
import random
import time

# Set up the screen
screen = turtle.Screen()
screen.bgcolor("black")
screen.title("Turtle Graphics")

# Create a turtle
pen = turtle.Turtle()
pen.speed(0)  # Fastest speed
pen.width(2)  # Set the pen width
turtle.tracer(0)  # Turn off the screen updates
pen.hideturtle()  # Hide the turtle


def run():

    # Define colors
    colors = []
    for i in range(random.randint(3, 10)):
        colors.append((random.random(), random.random(), random.random()))

    # Calculate the angle and step size based on the number of colors
    num_colors = len(colors)
    angle = 360 / num_colors + random.randint(1, 10)
    step_size = 360 / num_colors + random.randint(1, 10)

    # Draw a spiral
    for x in range(3600):
        pen.pencolor(colors[x % num_colors])  # Cycle through the colors
        pen.forward(
            x * step_size / 110
        )  # Move the turtle forward by a distance proportional to x and scaled by step_size
        pen.left(angle)  # Turn the turtle left by the calculated angle
        # the further along the less likely it is to update the screen
        if x < 1000:
            if x % 10 == 0:
                turtle.update()
        elif x < 2000:
            if x % 100 == 0:
                turtle.update()
        else:
            if x % 1000 == 0:
                turtle.update()
    turtle.update()
    # Hide the turtle
    pen.hideturtle()


while True:
    run()
    time.sleep(1)
    # reset the turtle and screen
    pen.clear()
    pen.reset()

# Keep the window open until it's closed by the user
turtle.done()
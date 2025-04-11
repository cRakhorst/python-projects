# make a for loop that checks every number (untill 360) and looks if i * something = 360

def is_whole(n):
    return n % 1 == 0

for i in range (1, 360):
    number = is_whole(360 / i)
    checkedNumber = 360 / i
    if (number):
        print('number:', i, 'is viable')
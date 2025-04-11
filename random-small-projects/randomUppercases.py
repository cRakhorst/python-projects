import random

#make script that takes a string and randomises the uppercases in the string
def randomise_uppercase(s):
    chars = list(s)
    for i in range(len(chars)):
        if i > 0 and chars[i - 1].isupper():
            if random.random() < 0.1:
                chars[i] = chars[i].upper()
        else:
            if random.random() < 0.5:
                chars[i] = chars[i].upper()
    return ''.join(chars)

print(randomise_uppercase("minutes later"))
import random

random_numbers = [int(random.random() * 200 + 1) for _ in range(25)]
random_numbers.sort()

for number in random_numbers:
    print(number)
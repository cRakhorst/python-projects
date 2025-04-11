# make a coin flip a set times and count the streak of heads and tails
import random

ceiling = 10000000
ceilingText = f"{ceiling:,}".replace(",", ".")

streakHeads = 0
streakTails = 0
heads = 0
tails = 0
for i in range (1, ceiling):
    result = round(random.random())
    if result == 0:
        heads += 1
        tails = 0
        if heads > streakHeads:
            streakHeads = heads
            print('streak heads:', streakHeads, 'iterations left:', ceiling - i)
    elif result == 1:
        tails += 1
        heads = 0
        if tails > streakTails:
            streakTails = tails
            print('streak tails:', streakTails, 'iterations left:', ceiling - i)

print('streak heads:', streakHeads,'streak tails:', streakTails, 'iterations completed:', ceilingText)

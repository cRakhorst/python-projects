from functools import cache

P, _, *D = open('day19.txt').read().split('\n')

@cache
def count(d):
    return d == '' or sum(count(d.removeprefix(p))
        for p in P.split(', ') if d.startswith(p))

for type in bool, int:
    print(sum(map(type, map(count, D))))
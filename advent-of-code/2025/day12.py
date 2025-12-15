print(sum(1 for r in [[int(n) for n in l.strip().replace('x',' ').replace(':','').split()]
for l in open('advent-of-code/2025/inputs/day12.txt', 'r') if 'x' in l]
if sum(r[2:])*9<=r[0]*r[1]))
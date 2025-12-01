import itertools

with open('day25.txt') as f:
    patterns = [item.splitlines() for item in f.read().split('\n\n')]
    
patterns = [{(i,j) for i,line in enumerate(pattern) for j,char in enumerate(line) if char=='#'} for pattern in patterns]

count = 0
for pattern1,pattern2 in itertools.combinations(patterns,2):
    if not set.intersection(pattern1,pattern2):
        count += 1

print(count)
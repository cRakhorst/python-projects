with open('day9.txt') as f:
    rawinput = f.read()

lengths = [int(num) for num in rawinput]

grid = [i//2 if i%2==0 else -1 for i,num in enumerate(lengths) for _ in range(num)]

while -1 in grid:
    if grid[-1] == (-1):
        grid.pop()
    else:
        index = grid.index(-1)
        grid[index] = grid.pop()

answer = sum(i*num for i,num in enumerate(grid))
print(answer)
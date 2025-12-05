import copy

file = 'advent-of-code/2025/inputs/day4.txt'
with open(file, 'r') as f:
    grid = [list(line.strip()) for line in f.readlines()]

rows = len(grid)
cols = len(grid[0])

directions = [
    (-1, -1), (-1, 0), (-1, 1),
    ( 0, -1),          ( 0, 1),
    ( 1, -1), ( 1, 0), ( 1, 1)
]

def count_surrounding_at(x, y):
    return sum(
        1 for dx, dy in directions
        if 0 <= x+dx < rows and 0 <= y+dy < cols and grid[x+dx][y+dy] == '@'
    )

def part1():
    count = 0
    for i in range(rows):
        for j in range(cols):
            if grid[i][j] == '@' and count_surrounding_at(i, j) < 4:
                count += 1
    return count


def part2():
    local_grid = copy.deepcopy(grid)   # <-- belangrijk

    rounds = 0
    total_removed = 0

    while True:
        to_remove = []

        for i in range(rows):
            for j in range(cols):
                if local_grid[i][j] == '@':
                    count = sum(
                        1 for dx, dy in directions
                        if 0 <= i+dx < rows and 0 <= j+dy < cols and local_grid[i+dx][j+dy] == '@'
                    )

                    if count < 4:
                        to_remove.append((i, j))

        if not to_remove:
            break

        for i, j in to_remove:
            local_grid[i][j] = '.'
            total_removed += 1

        rounds += 1

    return total_removed


print(part1())
print(part2())
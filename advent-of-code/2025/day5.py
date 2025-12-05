file = 'advent-of-code/2025/inputs/day5.txt'
with open(file, 'r') as f:
    content = f.read()

set1, set2 = content.strip().split("\n\n")

ranges = set1.split()
available = list(map(int, set2.split()))

def part1():
    answer = 0
    spoiled = []
    for r in ranges:
        a, b = map(int, r.split('-'))
        for num in available:
            if a <= num <= b and num not in spoiled:
                answer += 1
                spoiled.append(num)

    return answer

def slow():
    answer = 0
    safe = []
    for r in ranges:
        a, b = map(int, r.split('-'))
        for num in range(b + 1):
            if a <= num <= b and num not in safe:
                answer += 1
                safe.append(num)
                print("safe:", num)

    return answer

def slow2():
    safe = set()

    for r in ranges:
        a, b = map(int, r.split('-'))
        for num in range(a, b + 1):
            safe.add(num)
            print(num)

    return len(safe)

def part2():
    intervals = []

    for r in ranges:
        a, b = map(int, r.split('-'))
        intervals.append((a, b))

    # sorteren op beginwaarde
    intervals.sort()

    merged = []
    current_start, current_end = intervals[0]

    for start, end in intervals[1:]:
        if start <= current_end + 1:   # overlappend / aansluitend
            current_end = max(current_end, end)
        else:
            merged.append((current_start, current_end))
            current_start, current_end = start, end

    merged.append((current_start, current_end))

    # aantal getallen tellen
    return sum(end - start + 1 for start, end in merged)




print("Part 1:", part1())
print("Part 2:", part2())
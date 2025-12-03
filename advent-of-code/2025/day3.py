file = 'advent-of-code/2025/inputs/day3.txt'
with open(file, 'r') as f:
    content = f.read()

content = content.split('\n')

def part1():
    answer = 0

    for item in content:
        max_seen = -1
        best = -1

        for ch in item:
            d = int(ch)
            if max_seen >= 0:
                cand = max_seen * 10 + d
                if cand > best:
                    best = cand

            if d > max_seen:
                max_seen = d

        answer += best

    return answer
    

def best_number_from_string(s, k):
    stack = []
    n = len(s)

    for i, ch in enumerate(s):
        d = int(ch)

        while stack and stack[-1] < d and len(stack) + (n - i) > k:
            stack.pop()

        if len(stack) < k:
            stack.append(d)

    return int("".join(map(str, stack)))

def part2():
    answer = 0

    for item in content:
        answer += best_number_from_string(item, 12)

    return answer

print(part1())
print(part2())
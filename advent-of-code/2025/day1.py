file = 'advent-of-code/2025/inputs/day1.txt'
with open(file, 'r') as f:
    content = f.read()

indexes = content.split("\n")

def part1():
    answer = 0
    start = 50
    current = 0 + start
    for index in indexes:
        if index.__contains__("L"):
            value = int(index[1:])
            current -= value
            while (current < 0):
                current += 100
            if (current == 0):
                answer += 1
        
        if index.__contains__("R"):
            value = int(index[1:])
            current += value
            while (current > 99):
                current -= 100
            if (current == 0):
                answer += 1
    return answer

def part2():
    answer = 0
    current = 50

    for index in indexes:
        value = int(index[1:])
        old = current

        if index.startswith("L"):
            total = current - value
            start_zero = old != 0

            if total == 0:
                answer += 1
            elif total < 0:
                answer += total // -100 + start_zero

            while total < 0:
                total += 100
            current = total

        elif index.startswith("R"):
            total = current + value

            if total == 0:
                answer += 1
            elif total >= 100:
                answer += total // 100

            while total >= 100:
                total -= 100
            current = total

    return answer


print("answer part 1: ", part1())
print("answer part 2: ", part2())
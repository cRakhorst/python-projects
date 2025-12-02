import numpy as np

file = 'advent-of-code/2025/inputs/day2.txt'
with open(file, 'r') as f:
    content = f.read().strip()

inputs = content.split(',')

def part1():
    answer = 0

    for item in inputs:

        bounds = np.fromstring(item.strip(), dtype=int, sep='-')
        low = bounds[0]
        high = bounds[1]

        for i in range(low, high + 1):
            s = str(i)

            if len(s) % 2 != 0:
                continue

            mid = len(s) // 2
            first = s[:mid]
            second = s[mid:]

            if first == second:
                answer = answer + i

    return answer

def is_repeated_sequence(n):
    s = str(n)
    length = len(s)

    for size in range(1, length // 2 + 1):
        if length % size == 0:
            pattern = s[:size]
            if pattern * (length // size) == s:
                return True

    return False

def part2():
    answer = 0

    for item in inputs:

        if '-' not in item:
            continue

        low, high = map(int, item.strip().split('-'))

        for i in range(low, high + 1):
            s = str(i)
            length = len(s)

            # probeer elke mogelijke pattern-lengte
            for size in range(1, length // 2 + 1):

                if length % size != 0:
                    continue

                pattern = s[:size]
                repetitions = length // size

                if pattern * repetitions == s:
                    answer += i   # TEL HET GETAL OP (zoals in part1)
                    break          # stop na eerste match

    return answer


def read_input(filename: str):
  with open(filename, 'r') as file:
    return [line.strip() for line in file.readlines()]
  
def get_ranges(data):
  results = []
  ranges = data[0].split(',')
  for range in ranges:
    start, end = range.split('-')
    results.append((int(start), int(end)))
  return results

if __name__ == "__main__":
  input_data = read_input('advent-of-code/2025/inputs/day2.txt')
  ranges = get_ranges(input_data)
  print(part1())
  print(part2())

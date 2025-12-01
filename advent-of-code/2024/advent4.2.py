import re

example = '''
MMMSXXMASM
MSAMXMSMSA
AMXSXMAAMM
MSAMASMSMX
XMASAMXAMM
XXAMMXXAMA
SMSMSASXSS
SAXAMASAAA
MAMMMXMMMM
MXMXAXMASX'''.strip()

with open('day_4.txt') as f:
    real_input = ''.join(f.readlines()).strip()


def xmases(wordsearch):
    lines = list(wordsearch.splitlines())
    len_line = len(lines[0])
    flattened_lines = '.'.join(lines)

    yield from re.finditer('XMAS', flattened_lines)
    yield from re.finditer(rf'X(?=.{{{len_line-1}}}M.{{{len_line-1}}}A.{{{len_line-1}}}S)', flattened_lines)
    yield from re.finditer(rf'X(?=.{{{len_line}}}M.{{{len_line}}}A.{{{len_line}}}S)', flattened_lines)
    yield from re.finditer(rf'X(?=.{{{len_line+1}}}M.{{{len_line+1}}}A.{{{len_line+1}}}S)', flattened_lines)
    yield from re.finditer('SAMX', flattened_lines)
    yield from re.finditer(rf'S(?=.{{{len_line-1}}}A.{{{len_line-1}}}M.{{{len_line-1}}}X)', flattened_lines)
    yield from re.finditer(rf'S(?=.{{{len_line}}}A.{{{len_line}}}M.{{{len_line}}}X)', flattened_lines)
    yield from re.finditer(rf'S(?=.{{{len_line+1}}}A.{{{len_line+1}}}M.{{{len_line+1}}}X)', flattened_lines)


if __name__ == '__main__':
    print(sum(1 for _ in xmases(example)))
    print(sum(1 for _ in xmases(real_input)))


def x_mases(wordsearch):
    lines = list(wordsearch.splitlines())
    len_line = len(lines[0])
    flattened_lines = '.'.join(lines)

    yield from re.finditer(rf'M(?=.S.{{{len_line-1}}}A.{{{len_line-1}}}M.S)', flattened_lines)
    yield from re.finditer(rf'M(?=.M.{{{len_line-1}}}A.{{{len_line-1}}}S.S)', flattened_lines)
    yield from re.finditer(rf'S(?=.M.{{{len_line-1}}}A.{{{len_line-1}}}S.M)', flattened_lines)
    yield from re.finditer(rf'S(?=.S.{{{len_line-1}}}A.{{{len_line-1}}}M.M)', flattened_lines)


if __name__ == '__main__':
    print(sum(1 for _ in x_mases(example)))
    print(sum(1 for _ in x_mases(real_input)))
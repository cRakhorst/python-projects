robot_r, robot_c = -1, -1
 
def try_to_move():
  global robot_r
  global robot_c
  new_r, new_c = robot_r + dr, robot_c + dc
  if grid[new_r][new_c] == ".":
    grid[robot_r][robot_c] = "."
    grid[new_r][new_c] = "@"
    robot_r, robot_c = new_r, new_c
    return
  if grid[new_r][new_c] == "#":
    return
  new_r2, new_c2 = new_r, new_c
  while True:
    new_r2 += dr
    new_c2 += dc
    if grid[new_r2][new_c2] == "#":
      break
    if grid[new_r2][new_c2] == ".":
      grid[robot_r][robot_c] = "."
      grid[new_r][new_c] = "@"
      robot_r, robot_c = new_r, new_c
      grid[new_r2][new_c2] = "O"
      break
  return
 
grid = []
directions = ""
 
found_blank_line = False
r = 0
file = open("day15.txt", "r")
for line in file:
  line = line.replace("\n", "")
  if line == "":
    found_blank_line = True
    continue
  if found_blank_line:
    directions += line
    continue
  row = []
  c = 0
  for character in line:
    row.append(character)
    if character == "@":
      robot_r, robot_c = r, c
    c += 1
  grid.append(row)
  r += 1
 
for character in directions:
  dr, dc = -2, -2
  if character == "^":
    dr, dc = -1, 0
  if character == "v":
    dr, dc = 1, 0
  if character == "<":
    dr, dc = 0, -1
  if character == ">":
    dr, dc = 0, 1
  if dr == -2:
    continue
  try_to_move()
 
total = 0
for r in range(len(grid)):
  for c in range(len(grid[0])):
    if grid[r][c] == "O":
      total += 100 * r + c
print (total)
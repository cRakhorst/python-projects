## P1
carte = [ ]
dir = 0+1j

with open('day6.txt','r') as f:
    for ligne in f.read().splitlines():
        carte.append(ligne)

carte.reverse() ## I'm a mathematician, vertical axis goes up please...
amax = len(carte[0])
bmax = len(carte)

for a,ligne in enumerate(carte):
    for b in range(len(carte[a])):
        if carte[b][a] == '^':
            start = complex(a,b)
            break

def get(carte, pos, dir):
    npos = pos + dir
    return carte[int(npos.imag)][int(npos.real)]

def isvalid(pos):
    a, b = int(pos.real), int(pos.imag)
    return 0 <= b < bmax and 0 <= a < amax


pos = start
visited = set([start])
while isvalid(pos+dir):
    if get(carte,pos,dir) in '.^':
        pos = pos + dir
        visited.add(pos)
    elif get(carte,pos,dir) == '#':
        dir = dir*(-1j)

print('Part 1 :', len(visited))

oldvisited = visited.copy()
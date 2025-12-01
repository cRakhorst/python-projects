from bisect import bisect

data = [*map(eval, open('day18.txt'))]

def path(i):
    seen = {*data[:i]}
    todo = [(0, (0,0))]

    for dist, (x,y) in todo:
        if (x,y) == (70,70): return dist

        for x,y in (x,y+1), (x,y-1), (x+1,y), (x-1,y):
            if (x,y) not in seen and 0<=x<=70 and 0<=y<=70:
                todo.append((dist+1, (x,y)))
                seen.add((x,y))
    return 1e9

print(path(1024))

print(data[bisect(range(len(data)), 1e9-1, key=path)-1])
D = [(i//2+1 if i%2 else 0, int(d)) for i,d in
        enumerate(open('day9.txt').read(), 1)]

for i in range(len(D))[::-1]:
    for j in range(i):
        i_data, i_size = D[i]
        j_data, j_size = D[j]

        if i_data and not j_data and i_size <= j_size:
            D[i] = (0, i_size)
            D[j] = (0, j_size - i_size)
            D.insert(j, (i_data, i_size))


flatten = lambda x: [x for x in x for x in x]

print(sum(i*(c-1) for i,c in enumerate(flatten(
    [d]*s for d,s in D)) if c))
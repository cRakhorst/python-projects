from random import *

ammount = 10

test_array = [randint(1, 100) for i in range(ammount)]


#bubble sort algorithm    

def bubble_sort(array):
    print(array)
    n = len(array)

    for i in range(n):
        already_sorted = True
        for j in range(n - i - 1):
            if array[j] > array[j + 1]:
                array[j], array[j + 1] = array[j + 1], array[j]
                print(array)
                already_sorted = False
        if already_sorted:
            break
    return array

# own algorithm
# sort first five elements of array
# sort next five elements of array untill all sets of 5 are sorted
# sort the first 10 elements of the array
# sort the next 10 elements of the array untill all sets of 10 are sorted
# sort the first 15 elements of the array
# continue untill all elements are sorted

def own_sort(array):
    print(array)
    n = len(array)
    for i in range(0, n, ammount):
        for j in range(i, n, ammount):
            if j + ammount > n:
                break
            array[i:j + ammount] = bubble_sort(array[i:j + ammount])
            print(array)
    return array

print(own_sort(test_array))
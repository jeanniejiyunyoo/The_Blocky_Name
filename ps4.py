from typing import List


def func(lst: List[int]) -> (int, int, int):
    n = len(lst)
    i = 0
    j = 1
    count1 = 0
    count2 = 0
    count3 = 0
    while i < n:
        count1 += 1
        if lst[i] >= 0:
            i = i + j
            count3 += 1
        else:
            lst[i] = abs(lst[i])
            i = 0
            j = j * 2
            count2 += 1
    return count1, count2, count3


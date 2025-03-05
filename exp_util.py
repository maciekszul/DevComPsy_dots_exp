import numpy as np


def check_equal(a):
    """
    returns boolean if every element in iterable is equal
    """
    try:
        a = iter(a)
        first = next(a)
        return all(first == rest for rest in a)
    except StopIteration:
        return True


def search_n(a, n):
    """
    search for n repeating numbers
    a = iterable
    n = number of repeating elements
    """
    check = []
    carrier = a[n-1:]
    for index, value in enumerate(carrier):
        check = check_equal(a[index: index+n])
        if check:
            break
    return check


def randomisation(c, n):
    """
    c - conditions dict
    n - number of repetitions
    """
    if isinstance(c, dict):
        c = np.tile(c.keys(), n)
    elif isinstance(c, np.ndarray):
        pass
    np.random.shuffle(c)
    while search_n(c, 4):
        np.random.shuffle(c)
    return c
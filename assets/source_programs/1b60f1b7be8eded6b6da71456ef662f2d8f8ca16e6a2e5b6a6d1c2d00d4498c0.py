import numpy as np

def score(item, bins):
    v1 = bins - item
    v2 = v1 ** 2
    v3 = -v2
    return v3

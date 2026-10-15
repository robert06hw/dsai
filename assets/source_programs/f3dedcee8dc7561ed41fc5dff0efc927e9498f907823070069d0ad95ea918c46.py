import numpy as np

def score(item, bins):
    v1 = bins - item
    v2 = v1 * v1
    return -v2

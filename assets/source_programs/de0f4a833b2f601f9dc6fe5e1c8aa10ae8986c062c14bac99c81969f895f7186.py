import numpy as np

def score(item, bins):
    x = bins - item
    x2 = x * x
    return -((x * x2 - 25.0 * x2) * (x2 - 25.0 * x2))

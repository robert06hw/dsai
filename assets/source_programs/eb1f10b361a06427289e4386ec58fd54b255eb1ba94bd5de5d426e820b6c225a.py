import numpy as np

def score(item, bins):
    diff = bins - item
    squared_diff = diff * diff
    return -squared_diff + 25.0

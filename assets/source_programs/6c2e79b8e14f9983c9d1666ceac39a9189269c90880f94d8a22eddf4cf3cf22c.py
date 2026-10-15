import numpy as np

def score(item, bins):
    diff = bins - item
    squared_diff = diff * diff
    squared_squared_diff = squared_diff * squared_diff
    return -squared_squared_diff

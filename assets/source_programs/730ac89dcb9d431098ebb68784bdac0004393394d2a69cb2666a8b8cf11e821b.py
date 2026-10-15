import numpy as np

def score(item, bins):
    squared_diffs = np.square(bins - item)
    squared_diffs = np.maximum(squared_diffs, 0)
    return np.sqrt(squared_diffs) + 25.0

import numpy as np

def score(item, bins):
    return np.maximum(bins - item, 0) * np.maximum(bins - item - 25, 0) * np.maximum(bins - item - 50, 0) * np.maximum(bins - item - 75, 0) * np.maximum(bins - item - 100, 0)

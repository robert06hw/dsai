import numpy as np

def score(item, bins):
    return np.maximum(bins - item, 0) * np.maximum(bins - item - 28.0, 0)

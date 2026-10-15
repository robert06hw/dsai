import numpy as np

def score(item, bins):
    return np.maximum(bins - item, 0) * np.maximum(bins - item - 25.0, 0) ** 2

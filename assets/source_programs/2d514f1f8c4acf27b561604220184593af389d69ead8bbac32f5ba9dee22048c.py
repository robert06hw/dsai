import numpy as np

def score(item, bins):
    return np.maximum(bins - item, 0) * np.maximum(bins + 1, 0) * np.maximum(bins - 15.0, 0)

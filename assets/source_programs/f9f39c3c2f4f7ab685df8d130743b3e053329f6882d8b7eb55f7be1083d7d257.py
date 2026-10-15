import numpy as np

def score(item, bins):
    return np.maximum(bins - item - 18.0, 0) ** 2 / (bins + 1.0)

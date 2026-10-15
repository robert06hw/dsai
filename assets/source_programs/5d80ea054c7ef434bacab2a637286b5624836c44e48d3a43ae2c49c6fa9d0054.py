import numpy as np

def score(item, bins):
    return np.maximum(0, bins - item - 15.0) * (bins - item - 15.0 + 1.0)

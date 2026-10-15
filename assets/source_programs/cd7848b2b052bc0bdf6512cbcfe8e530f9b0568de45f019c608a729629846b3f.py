import numpy as np

def score(item, bins):
    return -np.minimum(np.minimum(bins - item, 0) * np.maximum(bins - item - 25.0, 0) * (bins - item) * np.maximum(bins - item - 25.0, 0), 0)

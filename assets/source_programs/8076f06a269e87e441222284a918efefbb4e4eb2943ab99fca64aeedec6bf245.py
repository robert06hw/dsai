import numpy as np

def score(item, bins):
    return np.maximum(0, bins - item) * np.maximum(0, bins - item - 25.0) * np.maximum(0, bins - item - 25.0) * np.maximum(0, bins - item - 25.0) * (bins - item)

import numpy as np

def score(item, bins):
    capacity = np.full_like(bins, 100)
    return np.maximum(0, (capacity - bins - item) - 28.0) * np.maximum(0, (capacity - bins - item) - 28.0)

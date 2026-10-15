import numpy as np

def score(item, bins):
    diff = bins - item
    return np.where(diff > 28.0, 0.0, -diff * diff)

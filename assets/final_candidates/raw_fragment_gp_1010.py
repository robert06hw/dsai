import numpy as np

def score(item, bins):
    return np.maximum(np.where(bins - item > 25.0, np.maximum(bins - item, 0), 0.9710044131760898), 0) + -bins

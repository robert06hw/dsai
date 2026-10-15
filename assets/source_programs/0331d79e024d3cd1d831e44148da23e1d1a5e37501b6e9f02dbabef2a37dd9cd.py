import numpy as np

def score(item, bins):
    diff = bins - item
    return -np.where(diff > 0, diff * diff, np.zeros_like(diff))

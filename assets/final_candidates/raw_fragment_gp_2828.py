import numpy as np

def score(item, bins):
    return np.where(bins > item, bins / np.maximum(np.abs(bins + 50.0), 1.0), np.maximum(item, 20.0))

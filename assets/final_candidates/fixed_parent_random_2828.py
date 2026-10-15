import numpy as np

def score(item, bins):
    return np.where(np.logical_and(bins > item, bins > item), (bins - item) / np.maximum(np.abs(-bins), 1.0), np.maximum(item, 20.0))

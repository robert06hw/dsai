import numpy as np

def score(item, bins):
    return np.where(np.logical_and(bins > item, bins > item), np.minimum(bins - item, bins), np.maximum(item, 54.743339093865025))

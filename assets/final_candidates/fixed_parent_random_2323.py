import numpy as np

def score(item, bins):
    return np.where((bins > item) | (bins > item), (np.log(np.maximum(bins - item, 0) + 1e-10) - item) * bins, np.where(item > 0, item, item))

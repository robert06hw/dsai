import numpy as np

def score(item, bins):
    return np.maximum(np.minimum(bins - item, bins), 0) * (bins - item) ** 2

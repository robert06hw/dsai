import numpy as np

def score(item, bins):
    return -np.minimum(bins - item, np.maximum(np.full_like(bins - item, -25.0), bins - item))

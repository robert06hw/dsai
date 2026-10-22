import numpy as np

def score(item, bins):
    return (np.where(bins - item > 0, np.ones_like(bins) - item, 18.0) - item) * ((np.maximum(bins - item, 0) - 40.0) ** 2 - 0.0)

import numpy as np

def score(item, bins):
    residual = bins - item
    bins_used = residual > 0
    return np.where(bins_used, residual, -bins)

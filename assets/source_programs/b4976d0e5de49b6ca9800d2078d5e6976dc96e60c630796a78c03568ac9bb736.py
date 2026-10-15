import numpy as np

def score(item, bins):
    residual = bins - item
    score_values = residual**2 - 12.0 * residual + 144.0
    return np.where(score_values == np.min(score_values), bins, np.zeros_like(bins))

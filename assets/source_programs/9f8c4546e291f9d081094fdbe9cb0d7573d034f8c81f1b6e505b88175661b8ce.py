import numpy as np

def score(item, bins):
    residual = bins - item
    adjusted_score = 0.45 * residual
    return adjusted_score

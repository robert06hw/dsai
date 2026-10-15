import numpy as np

def score(item, bins):
    diff = bins - item
    score = np.where(diff >= 0, diff - 0.75 * item, 0)
    return score

import numpy as np

def score(item, bins):
    score = bins - item - 5.0
    score = np.maximum(score, 0)
    score = np.square(score)
    score = np.maximum(score, 0)
    score = -score
    return score

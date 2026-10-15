import numpy as np

def score(item, bins):
    scores = bins - item
    scores = np.where(scores >= 0, scores ** 2, 0)
    return scores

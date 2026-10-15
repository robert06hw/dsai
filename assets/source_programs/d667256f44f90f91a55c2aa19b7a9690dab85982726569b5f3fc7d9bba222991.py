import numpy as np

def score(item, bins):
    scores = bins - item
    scores = np.where(scores > 0, scores - 5.0, 0.0)
    scores = scores ** 2
    return scores

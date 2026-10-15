import numpy as np

def score(item, bins):
    scores = np.maximum(0, bins - item) - 0.75 * item
    return scores

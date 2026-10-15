import numpy as np

def score(item, bins):
    score = bins - item - 0.75 * item
    return -np.square(score)

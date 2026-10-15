import numpy as np

def score(item, bins):
    scores = (bins - item) - (1.25 * item)
    return -np.square(scores)

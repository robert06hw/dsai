import numpy as np

def score(item, bins):
    v1 = (bins - item)
    bin_scores = np.where(v1 > 0, v1, 0)
    return bin_scores

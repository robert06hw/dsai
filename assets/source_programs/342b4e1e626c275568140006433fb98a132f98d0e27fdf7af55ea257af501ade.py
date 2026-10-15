import numpy as np

def score(item, bins):
    distance_1 = 100.0 - bins
    mask_2 = bins >= item
    score_3 = distance_1 * mask_2
    return score_3

import numpy as np

def score(item, bins):
    capacity = 100
    bin_scores = (bins - item) * (bins >= item)
    return bin_scores

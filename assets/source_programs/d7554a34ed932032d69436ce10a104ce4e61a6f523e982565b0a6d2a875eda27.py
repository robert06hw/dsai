import numpy as np

def score(item, bins):
    scores = bins * (bins - item) * (bins - item)
    return scores

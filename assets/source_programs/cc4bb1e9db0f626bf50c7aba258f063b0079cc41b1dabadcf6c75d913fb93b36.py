import numpy as np

def score(item, bins):
    score = -(((bins - item) - 12.0) * ((bins - item) - 12.0))
    return np.where(bins >= item, score, 0)

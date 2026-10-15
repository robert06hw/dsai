import numpy as np

def score(item, bins):
    score = -(((bins - item) ** 2) ** 2 - 25.0) * (bins - item) ** 2
    return np.where(score == np.max(score), bins, np.zeros_like(bins))

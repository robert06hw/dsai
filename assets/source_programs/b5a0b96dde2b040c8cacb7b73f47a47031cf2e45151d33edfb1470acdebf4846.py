import numpy as np

def score(item, bins):
    scores = (-(((bins - item) * (bins - item)) / (item + 1.0))) + (0.3 * (bins - item))
    return np.argsort(-scores)[::-1] // 100

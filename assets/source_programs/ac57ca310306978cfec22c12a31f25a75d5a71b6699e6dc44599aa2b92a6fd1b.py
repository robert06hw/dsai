import numpy as np

def score(item, bins):
    scores = -(np.maximum(bins - item, 0) * np.log(bins - item + 1e-10)) + 25.0
    return np.maximum(scores - np.argmax(scores), 0)

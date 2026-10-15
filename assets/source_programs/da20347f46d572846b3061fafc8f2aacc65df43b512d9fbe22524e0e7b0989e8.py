import numpy as np

def score(item, bins):
    score_array = -(((bins - item) - 0.75 * item) ** 2)
    return score_array

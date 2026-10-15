import numpy as np

def score(item, bins):
    score = -(bins - item) * (bins - item - 5.0) * (bins - item - 10.0)
    return score

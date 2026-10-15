import numpy as np

def score(item, bins):
    score = -((bins - item) ** 2)
    return score

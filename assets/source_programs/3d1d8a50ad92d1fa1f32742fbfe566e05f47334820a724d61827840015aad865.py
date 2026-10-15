import numpy as np

def score(item, bins):
    scores = -((bins - item) ** 2 * ((bins - item) ** 2 - 25.0))
    return scores

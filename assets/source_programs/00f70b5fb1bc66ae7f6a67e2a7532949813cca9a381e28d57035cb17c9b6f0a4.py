import numpy as np

def score(item, bins):
    scores = ((bins - item) - 20.0) * ((bins - item) - 20.0)
    return scores

import numpy as np

def score(item, bins):
    score = -(((bins - item) * ((bins - item) - 25.0)) * ((bins - item) * ((bins - item) - 25.0)))
    return score

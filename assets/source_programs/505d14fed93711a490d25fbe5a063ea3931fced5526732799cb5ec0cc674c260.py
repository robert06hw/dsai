import numpy as np

def score(item, bins):
    score = -(((bins - item) - (20.0 / (item + 1.0))) * ((bins - item) - (20.0 / (item + 1.0))))
    return score

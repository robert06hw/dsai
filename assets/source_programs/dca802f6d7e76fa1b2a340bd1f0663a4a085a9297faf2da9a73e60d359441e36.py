import numpy as np

def score(item, bins):
    capacity = 100.0
    diff = bins - item
    score = -(((diff - (item / (diff + 1.0))) * (diff - (item / (diff + 1.0)))))
    return score

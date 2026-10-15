import numpy as np

def score(item, bins):
    score = bins - item
    return -((score - (item / (score + 1.0))) ** 2)

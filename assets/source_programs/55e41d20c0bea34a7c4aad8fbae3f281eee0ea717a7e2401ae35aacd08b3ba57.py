import numpy as np

def score(item, bins):
    return -((bins - item) - 28.0) ** 2

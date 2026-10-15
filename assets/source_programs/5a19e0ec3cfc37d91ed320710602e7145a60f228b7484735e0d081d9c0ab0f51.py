import numpy as np

def score(item, bins):
    return -((bins - item) - 5.0) * ((bins - item) - 5.0)

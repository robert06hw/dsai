import numpy as np

def score(item, bins):
    return -((bins - item) - (item / ((bins - item) + 1.0))) * ((bins - item) - (item / ((bins - item) + 1.0)))

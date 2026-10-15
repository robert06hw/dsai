import numpy as np

def score(item, bins):
    return -((bins - item) - (0.25 * item)) * ((bins - item) - (0.25 * item))

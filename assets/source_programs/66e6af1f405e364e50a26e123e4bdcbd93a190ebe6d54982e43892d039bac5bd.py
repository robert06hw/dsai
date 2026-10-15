import numpy as np

def score(item, bins):
    return np.where(item > bins, np.inf, -((bins - item) - (item / ((bins - item) + 1.0))) * ((bins - item) - (item / ((bins - item) + 1.0))))

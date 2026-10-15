import numpy as np

def score(item, bins):
    return np.where(bins > item, bins, np.square(np.negative(83.50068842595658)))

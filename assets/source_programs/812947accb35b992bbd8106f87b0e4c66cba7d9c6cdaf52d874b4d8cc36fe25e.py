import numpy as np

def score(item, bins):
    bin_scores = -(((bins - item) - 40.0) * ((bins - item) - 40.0))
    return bin_scores

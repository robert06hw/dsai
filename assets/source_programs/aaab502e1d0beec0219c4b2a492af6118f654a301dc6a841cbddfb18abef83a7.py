import numpy as np

def score(item, bins):
    bins_less = bins - item
    bins_less_squared = bins_less * bins_less
    bins_scores = bins_less_squared - 28.0 * bins_less
    return bins_scores

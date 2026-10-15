import numpy as np

def score(item, bins):
    adjusted_bins = bins - item - 15.0
    adjusted_bins_squared = adjusted_bins * adjusted_bins
    scores = (-adjusted_bins_squared) * (bins + 1.0)
    return scores

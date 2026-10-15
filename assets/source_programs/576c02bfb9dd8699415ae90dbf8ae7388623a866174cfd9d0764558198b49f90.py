import numpy as np

def score(item, bins):
    bins_to_right = bins - item
    bins_to_left = bins_to_right - 15.0
    squared_bins_to_left = bins_to_left * bins_to_left
    score = -squared_bins_to_left
    bins_to_left_plus_1 = bins_to_left + 1.0
    final_score = score * bins_to_left_plus_1
    return final_score

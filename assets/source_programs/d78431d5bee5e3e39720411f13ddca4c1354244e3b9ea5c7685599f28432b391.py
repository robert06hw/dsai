import numpy as np

def score(item, bins):
    bin_diffs = bins - item
    squared_diffs = bin_diffs * bin_diffs
    return -squared_diffs

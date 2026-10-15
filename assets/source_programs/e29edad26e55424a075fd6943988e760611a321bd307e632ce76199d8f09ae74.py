import numpy as np

def score(item, bins):
    # Calculate the score for each bin using a vectorized approach
    scores = (bins - item) * (bins - item)
    return -scores

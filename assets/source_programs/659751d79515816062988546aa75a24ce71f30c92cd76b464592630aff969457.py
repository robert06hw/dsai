import numpy as np

def score(item, bins):
    capacity = 100
    bins_remaining = bins >= item
    bins_used = capacity - bins_remaining
    scores = bins_used - bins_remaining * item
    return scores

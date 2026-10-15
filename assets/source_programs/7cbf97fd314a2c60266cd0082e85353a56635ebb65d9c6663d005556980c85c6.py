def score(item, bins):
    return -((bins - item) * bins) + bins

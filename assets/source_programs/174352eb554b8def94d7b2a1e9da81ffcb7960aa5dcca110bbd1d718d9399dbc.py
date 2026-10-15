def score(item, bins):
    diff = bins - item
    valid_bins = diff >= 0
    scores = np.where(valid_bins, diff ** 2, 0)
    return -scores

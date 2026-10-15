def score(item, bins):
    bins_minus_item = bins - item
    bins_minus_item_minus_25 = bins_minus_item - 25.0
    scores = np.maximum(np.maximum(bins_minus_item, bins_minus_item_minus_25), 0)
    return scores

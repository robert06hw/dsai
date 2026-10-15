def score(item, bins):
    score = np.where(bins - item >= 0, (bins - item) * (bins - item) * (bins - item) * (bins - item), 0)
    return score

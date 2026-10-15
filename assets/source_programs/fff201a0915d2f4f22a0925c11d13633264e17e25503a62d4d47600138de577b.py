def score(item, bins):
    score = -(bins - item) * np.maximum(0, bins - item - 25.0)
    return score

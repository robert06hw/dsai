def score(item, bins):
    scores = bins - item
    scores = np.where(scores > 5.0, scores - 5.0, scores)
    scores = np.where(scores < 0, 0, scores)
    scores = scores * scores
    scores = -scores
    return scores

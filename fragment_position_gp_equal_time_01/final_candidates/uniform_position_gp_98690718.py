def score(item, bins):
    return np.where(bins > item, np.minimum(bins - item - 22.832035253623225 - item, bins - item), np.argmax(bins - item - 15.0))

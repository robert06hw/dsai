def score(item, bins):
    return -np.where((bins - item) >= 0, (bins - item) - (0.75 * item), 0)

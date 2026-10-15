def score(item, bins):
    v2 = (item + 1.0)
    v3 = (20.0 / v2)
    v6 = -(v3 * (bins - item) * (bins - item))
    return v6

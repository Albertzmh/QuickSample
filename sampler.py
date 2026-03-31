import random
import math


def get_all_features(layer):
    """Return list of all features in the layer."""
    return list(layer.getFeatures())


def sample_first_n(layer, n):
    """Return the first N features."""
    features = get_all_features(layer)
    return features[:n]


def sample_last_n(layer, n):
    """Return the last N features."""
    features = get_all_features(layer)
    return features[-n:] if n <= len(features) else features


def sample_random_n(layer, n, seed=None):
    """Return N randomly sampled features."""
    features = get_all_features(layer)
    n = min(n, len(features))
    if seed is not None:
        random.seed(seed)
    return random.sample(features, n)


def sample_percentage(layer, pct, seed=None):
    """Return a random sample of pct% of features."""
    features = get_all_features(layer)
    n = max(1, math.floor(len(features) * pct / 100.0))
    n = min(n, len(features))
    if seed is not None:
        random.seed(seed)
    return random.sample(features, n)

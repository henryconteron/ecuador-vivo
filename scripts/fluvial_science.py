"""Auditable baseline methods; a spectral signal is never a cause or flow rate.

All arrays are native reflectance, band-major B2/B3/B4/B8/B11/B12.
Minimum-distance prototypes must be learned from independent manual references,
never from SCL or from the indices being evaluated.
"""
import numpy as np

METHODS = ("ndwi", "mndwi", "aweinsh", "aweish")
CLASSES = ("water_shallow", "water_deep", "sediment", "vegetation")


def ratio(a, b):
    valid = np.isfinite(a) & np.isfinite(b) & (a >= 0) & (b >= 0) & (a + b > 0)
    result = np.full(np.shape(a), np.nan, dtype=np.float32)
    np.divide(a - b, a + b, out=result, where=valid)
    return result


def signals(bands):
    if bands.shape[0] != 6:
        raise ValueError("Six reflectance bands required")
    blue, green, red, nir, swir1, swir2 = bands
    return {"ndwi": ratio(green, nir), "mndwi": ratio(green, swir1),
            "aweinsh": 4 * (green - swir1) - .25 * nir - 2.75 * swir2,
            "aweish": blue + 2.5 * green - 1.5 * (nir + swir1) - .25 * swir2,
            "ndti": ratio(red, green), "ndvi": ratio(nir, red)}


def votes(bands, valid, thresholds):
    if set(thresholds) != set(METHODS) or any(not np.isfinite(x) for x in thresholds.values()):
        raise ValueError("Four finite exploratory thresholds required")
    values = signals(bands)
    usable = valid.astype(bool) & np.all(np.isfinite(bands) & (bands >= 0), axis=0)
    usable &= np.all([np.isfinite(values[key]) for key in values], axis=0)
    count = np.sum([values[key] > thresholds[key] for key in METHODS], axis=0).astype(np.uint8)
    # -1 means no observation, 0/4 agreement, 1..3 disagreement. NOT confidence.
    return np.where(usable, count, -1).astype(np.int8)


def transitions(earlier, later):
    """0 NoData; 1 stable non-water; 2 stable water; 3 loss; 4 gain; 5 disputed.

Only unanimous four-method support counts as an exploratory water transition.
Absence of unanimous water is NOT a sediment or dry-bed classification.
"""
    if earlier.shape != later.shape:
        raise ValueError("Identical spatial grids required")
    out = np.zeros(earlier.shape, dtype=np.uint8)
    common = (earlier >= 0) & (later >= 0)
    out[common] = 5
    out[common & (earlier == 0) & (later == 0)] = 1
    out[common & (earlier == 4) & (later == 4)] = 2
    out[common & (earlier == 4) & (later == 0)] = 3
    out[common & (earlier == 0) & (later == 4)] = 4
    return out


def presence_frequency(classifications, valid):
    """Fraction among useful observations, not consecutive dry days or flow.

Missing observations contribute neither water nor absence. All missing => NaN.
"""
    if classifications.shape != valid.shape or classifications.ndim < 2:
        raise ValueError("Aligned time and pixel arrays required")
    if np.any(~np.isin(classifications[valid.astype(bool)], [0, 1])):
        raise ValueError("Useful classifications must be binary")
    count = valid.astype(bool).sum(axis=0)
    water = np.where(valid, classifications, 0).sum(axis=0)
    fraction = np.full(count.shape, np.nan, dtype=np.float32)
    np.divide(water, count, out=fraction, where=count > 0)
    return fraction, count


def fit_minimum_distance(features, labels):
    features = np.asarray(features)
    labels = np.asarray(labels)
    if features.ndim != 2 or features.shape[1] != 6 or len(labels) != len(features) or not np.isfinite(features).all():
        raise ValueError("Finite six-band reference features required")
    if set(labels) != set(CLASSES):
        raise ValueError("Independent examples of all four classes required")
    return np.stack([features[labels == label].mean(axis=0) for label in CLASSES])


def classify_minimum_distance(features, prototypes):
    if features.ndim != 2 or features.shape[1] != 6 or prototypes.shape != (4, 6) or not np.isfinite(features).all() or not np.isfinite(prototypes).all():
        raise ValueError("Six-band features and four finite prototypes required")
    return np.argmin(np.sum((features[:, None, :] - prototypes[None, :, :]) ** 2, axis=2), axis=1)


def water_metrics(actual, predicted):
    if actual.shape != predicted.shape or actual.size == 0:
        raise ValueError("Nonempty held-out references required")
    actual, predicted = actual.astype(bool), predicted.astype(bool)
    tp = int((actual & predicted).sum()); fp = int((~actual & predicted).sum())
    fn = int((actual & ~predicted).sum()); tn = int((~actual & ~predicted).sum())
    divide = lambda a, b: a / b if b else None
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn,
            "precision": divide(tp, tp + fp), "recall": divide(tp, tp + fn),
            "f1": divide(2 * tp, 2 * tp + fp + fn), "iou": divide(tp, tp + fp + fn)}

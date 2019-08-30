import numpy as np


def benjamini_hochberg(pvalues, FDR=0.05):
    pvalues = np.array(pvalues)
    if pvalues.size == 0:
        return np.nan
    sorted_values = np.sort(pvalues[np.logical_not(np.logical_or(np.isnan(pvalues), np.isinf(pvalues)))], axis=None)
    critical_values = np.arange(1, len(sorted_values) + 1) / len(sorted_values) * FDR
    idx = np.argwhere(sorted_values < critical_values).flatten()
    if idx.size == 0:
        return np.nan
    else:
        return sorted_values[idx[-1]]
